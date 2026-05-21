"""Monologue 재조립 — 동일 화자의 연속 발화를 묶어 OPIc 모놀로그 학습 단위로 만든다.

ADR-0004 참조: 백채널(짧은 응답)은 영구 제거하지 않고, 본 단계에서만 skip한다.
"""

from __future__ import annotations

import re

from scripttuner.preprocessing.ir import Monologue, Utterance

DEFAULT_BACKCHANNEL_WORDS: frozenset[str] = frozenset(
    {
        "okay",
        "ok",
        "yeah",
        "yep",
        "yes",
        "no",
        "right",
        "mhm",
        "mm",
        "uhhuh",
        "sure",
        "oh",
        "hm",
        "hmm",
        "gotcha",
        "good",
    }
)
"""기본 백채널 어휘. 소문자 + punctuation 제거 기준."""

DEFAULT_MIN_TOKENS = 30
DEFAULT_MAX_BACKCHANNEL_TOKENS = 3

_PAUSE_TOKEN_RE = re.compile(r"<pause:\w+>")
_WORD_RE = re.compile(r"\b\w+\b")


def _word_tokens(text: str) -> list[str]:
    """Pause 등 특수 토큰을 제거하고 word token만 추출 (소문자)."""
    stripped = _PAUSE_TOKEN_RE.sub("", text)
    return [m.group(0).lower() for m in _WORD_RE.finditer(stripped)]


def is_backchannel(
    text: str,
    *,
    backchannel_words: frozenset[str] = DEFAULT_BACKCHANNEL_WORDS,
    max_tokens: int = DEFAULT_MAX_BACKCHANNEL_TOKENS,
) -> bool:
    """텍스트가 백채널인지 판정한다.

    조건: word token 1~max_tokens 개이며, 모든 토큰이 백채널 사전에 속함.
    """
    tokens = _word_tokens(text)
    if not tokens or len(tokens) > max_tokens:
        return False
    return all(t in backchannel_words for t in tokens)


def build_monologues(
    utterances: list[Utterance],
    *,
    min_tokens: int = DEFAULT_MIN_TOKENS,
    backchannel_words: frozenset[str] = DEFAULT_BACKCHANNEL_WORDS,
    max_backchannel_tokens: int = DEFAULT_MAX_BACKCHANNEL_TOKENS,
) -> list[Monologue]:
    """Utterance 리스트에서 monologue를 재조립한다.

    Args:
        utterances: cleaned text 기준 utterance 리스트.
        min_tokens: 이 미만의 monologue는 필터링.
        backchannel_words: 백채널 어휘 사전.
        max_backchannel_tokens: 백채널로 간주할 최대 토큰 수.

    Returns:
        길이 필터를 통과한 Monologue 리스트.
    """
    monologues: list[Monologue] = []
    buf_speaker: str | None = None
    buf_source: str | None = None
    buf_texts: list[str] = []
    buf_ids: list[str] = []
    seq = 0

    def flush() -> None:
        nonlocal seq, buf_speaker, buf_source, buf_texts, buf_ids
        if not buf_texts or buf_speaker is None or buf_source is None:
            buf_speaker = None
            buf_source = None
            buf_texts = []
            buf_ids = []
            return
        text = " ".join(buf_texts).strip()
        text = re.sub(r"\s+", " ", text)
        n_tokens = len(_word_tokens(text))
        if n_tokens >= min_tokens:
            seq += 1
            file_stem = _file_stem_from_ids(buf_ids)
            monologue_id = f"{file_stem}#mono_{seq:04d}"
            monologues.append(
                Monologue(
                    source=buf_source,
                    monologue_id=monologue_id,
                    speaker=buf_speaker,
                    text=text,
                    utterance_ids=tuple(buf_ids),
                    n_tokens=n_tokens,
                )
            )
        buf_speaker = None
        buf_source = None
        buf_texts = []
        buf_ids = []

    for u in utterances:
        if buf_speaker is None:
            # 새 화자 시작
            buf_speaker = u.speaker
            buf_source = u.source
            buf_texts = [u.text]
            buf_ids = [u.utterance_id]
        elif u.speaker == buf_speaker:
            buf_texts.append(u.text)
            buf_ids.append(u.utterance_id)
        else:
            # 다른 화자
            if is_backchannel(
                u.text,
                backchannel_words=backchannel_words,
                max_tokens=max_backchannel_tokens,
            ):
                # 백채널: buffer 유지, 이 utterance는 무시
                continue
            # 본격 발화: 현재 buffer flush 후 새 화자로
            flush()
            buf_speaker = u.speaker
            buf_source = u.source
            buf_texts = [u.text]
            buf_ids = [u.utterance_id]

    flush()
    return monologues


def _file_stem_from_ids(ids: list[str]) -> str:
    """utterance_id 'SBC016#0001' → 'SBC016' 추출."""
    if not ids:
        return "unknown"
    return ids[0].split("#", 1)[0]
