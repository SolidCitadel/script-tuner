"""대상 모델 레지스트리 — 파인튜닝 model_key의 단일 진실원.

`model_key` → 모델 식별(`hf_id`) + 학습 데이터 형태(`format_kind`).

formatter(데이터 변환)는 `format_kind`만 필요하므로 `hf_id` 없이도 동작한다. 실제 학습(train)은
`hf_id`가 필요하며, 아직 확인되지 않은 키는 `hf_id=None`으로 두어 **formatting은 허용하되
training 시 명시적으로 막는다** (추론으로 repo id를 지어내지 않기 위함).

LoRA/양자화 등 학습 하이퍼파라미터는 실제 사용처(train.py)에 둔다 — 여기는 "이 모델이 무엇인가"만.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FormatKind = Literal["chat", "seq2seq"]


@dataclass(frozen=True)
class ModelSpec:
    """파인튜닝 대상 모델 하나의 명세."""

    key: str
    format_kind: FormatKind
    hf_id: str | None
    """HF repo id. None이면 아직 학습용으로 확인/연결되지 않은 키(formatting만 가능)."""


MODEL_SPECS: dict[str, ModelSpec] = {
    "gemma4-e4b": ModelSpec(
        key="gemma4-e4b",
        format_kind="chat",
        hf_id="unsloth/gemma-4-E4B-it-unsloth-bnb-4bit",
    ),
    "gemma4-e2b": ModelSpec(
        key="gemma4-e2b",
        format_kind="chat",
        hf_id="unsloth/gemma-4-E2B-it-unsloth-bnb-4bit",
    ),
    # T5Gemma 2 (encoder-decoder, seq2seq) — 1차 주력 계열. 크기별로 분리.
    # 270m/4b id는 HF에서 확인됨; 1b는 동일 명명 패턴(첫 사용 시 다운로드로 확정).
    "t5gemma2-270m": ModelSpec(
        key="t5gemma2-270m", format_kind="seq2seq", hf_id="google/t5gemma-2-270m-270m"
    ),
    "t5gemma2-1b": ModelSpec(
        key="t5gemma2-1b", format_kind="seq2seq", hf_id="google/t5gemma-2-1b-1b"
    ),
    "t5gemma2-4b": ModelSpec(
        key="t5gemma2-4b", format_kind="seq2seq", hf_id="google/t5gemma-2-4b-4b"
    ),
    # 비교용 후보 — HF repo id 미확인이라 formatting 전용(학습 연결 시 id 확인 후 채움).
    "qwen3-4b": ModelSpec(key="qwen3-4b", format_kind="chat", hf_id=None),
    "qwen3-1.7b": ModelSpec(key="qwen3-1.7b", format_kind="chat", hf_id=None),
}

MODEL_KEYS: frozenset[str] = frozenset(MODEL_SPECS)


def get_model_spec(model_key: str) -> ModelSpec:
    """키에 해당하는 모델 명세를 반환. 미지원 키면 ValueError."""
    try:
        return MODEL_SPECS[model_key]
    except KeyError as e:
        supported = ", ".join(sorted(MODEL_SPECS))
        raise ValueError(
            f"Unsupported model key {model_key!r}. Supported models: {supported}"
        ) from e


def model_format_kind(model_key: str) -> FormatKind:
    """모델의 학습 데이터 형태(chat/seq2seq)."""
    return get_model_spec(model_key).format_kind


def require_hf_id(model_key: str) -> str:
    """학습용 HF repo id를 반환. 아직 학습 연결이 안 된 키면 ValueError."""
    spec = get_model_spec(model_key)
    if spec.hf_id is None:
        raise ValueError(
            f"Model {model_key!r} has no HF id wired for training yet. "
            f"Confirm its repo id and set it in MODEL_SPECS."
        )
    return spec.hf_id
