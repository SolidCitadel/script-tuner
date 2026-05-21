from __future__ import annotations

from pathlib import Path

import pytest

from scripttuner.preprocessing import monologue
from scripttuner.preprocessing.chat import cleaner, parser
from scripttuner.preprocessing.ir import Utterance


def _u(speaker: str, text: str, *, seq: int = 0, source: str = "TEST") -> Utterance:
    return Utterance(
        source=source,
        utterance_id=f"FAKE#{seq:04d}",
        speaker=speaker,
        text=text,
    )


# ----- is_backchannel -----


def test_backchannel_single_word() -> None:
    assert monologue.is_backchannel("Okay")
    assert monologue.is_backchannel("yeah")
    assert monologue.is_backchannel("Mhm .")


def test_backchannel_multi_word_within_limit() -> None:
    # 토큰 수 ≤ 3, 모두 사전에 있음 (max_backchannel_tokens=3 기본)
    assert monologue.is_backchannel("yeah yeah yeah")


def test_not_backchannel_when_exceeds_token_limit() -> None:
    # 4 토큰
    assert not monologue.is_backchannel("yeah yeah yeah yeah")


def test_not_backchannel_when_contains_non_backchannel_word() -> None:
    assert not monologue.is_backchannel("yeah tape deck")


def test_pause_tokens_ignored_in_backchannel_detection() -> None:
    assert monologue.is_backchannel("<pause:short> Okay <pause:long>")


def test_empty_text_not_backchannel() -> None:
    assert not monologue.is_backchannel("")
    assert not monologue.is_backchannel(".")


# ----- build_monologues -----


def test_single_speaker_combines_consecutive_utterances() -> None:
    long_text = " ".join(["word"] * 35)
    utts = [
        _u("A", long_text[:100], seq=1),
        _u("A", long_text[100:], seq=2),
    ]
    monos = monologue.build_monologues(utts, min_tokens=10)
    assert len(monos) == 1
    assert monos[0].speaker == "A"
    assert monos[0].utterance_ids == ("FAKE#0001", "FAKE#0002")


def test_backchannel_skipped_buffer_kept() -> None:
    long_text_a1 = " ".join(["alpha"] * 20)
    long_text_a2 = " ".join(["beta"] * 20)
    utts = [
        _u("A", long_text_a1, seq=1),
        _u("B", "Okay .", seq=2),     # 백채널 → skip
        _u("A", long_text_a2, seq=3),  # A 발화 이어짐
    ]
    monos = monologue.build_monologues(utts, min_tokens=10)
    assert len(monos) == 1
    assert monos[0].speaker == "A"
    assert "FAKE#0002" not in monos[0].utterance_ids
    assert set(monos[0].utterance_ids) == {"FAKE#0001", "FAKE#0003"}


def test_non_backchannel_speaker_change_flushes() -> None:
    long_text = " ".join(["w"] * 35)
    utts = [
        _u("A", long_text, seq=1),
        _u("B", long_text, seq=2),  # 본격 발화 → flush
    ]
    monos = monologue.build_monologues(utts, min_tokens=10)
    assert len(monos) == 2
    assert monos[0].speaker == "A"
    assert monos[1].speaker == "B"


def test_min_tokens_filter() -> None:
    utts = [
        _u("A", "short reply", seq=1),  # 2 tokens
    ]
    monos = monologue.build_monologues(utts, min_tokens=30)
    assert monos == []


def test_n_tokens_excludes_pause_tokens() -> None:
    long_text = " ".join(["word"] * 35)
    utts = [_u("A", f"<pause:short> {long_text} <pause:long>", seq=1)]
    monos = monologue.build_monologues(utts, min_tokens=10)
    assert monos[0].n_tokens == 35


def test_monologue_id_format() -> None:
    long_text = " ".join(["w"] * 35)
    utts = [
        Utterance(
            source="SBCSAE",
            utterance_id="SBC016#0001",
            speaker="TAMM",
            text=long_text,
        ),
        Utterance(
            source="SBCSAE",
            utterance_id="SBC016#0005",
            speaker="TAMM",
            text=long_text,
        ),
    ]
    monos = monologue.build_monologues(utts, min_tokens=10)
    assert monos[0].monologue_id == "SBC016#mono_0001"
    assert monos[0].source == "SBCSAE"


# ----- 통합: SBC016.cha 전체 흐름 -----

_REAL_FILE = Path("datasets/sbcsae/SBC016.cha")


@pytest.mark.skipif(not _REAL_FILE.exists(), reason="SBC016.cha not downloaded")
def test_integration_sbc016_pipeline() -> None:
    _, utts = parser.parse(_REAL_FILE)
    cleaned = cleaner.clean(utts)
    monos = monologue.build_monologues(cleaned)

    # 일부 monologue가 추출됨
    assert len(monos) >= 5

    # 모든 monologue가 임계값 이상
    assert all(m.n_tokens >= monologue.DEFAULT_MIN_TOKENS for m in monos)

    # 화자는 SBC016에 등록된 화자 중 하나
    for m in monos:
        assert m.speaker in {"TAMM", "BRAD", "TODD", "JONA"}

    # monologue_id가 SBC016 prefix를 사용
    assert all(m.monologue_id.startswith("SBC016#mono_") for m in monos)
