from __future__ import annotations

import pytest

from scripttuner.training.registry import (
    MODEL_KEYS,
    get_model_spec,
    model_format_kind,
    require_hf_id,
)


def test_model_keys_match_specs() -> None:
    assert MODEL_KEYS == {
        "gemma4-e4b",
        "gemma4-e2b",
        "t5gemma2-270m",
        "t5gemma2-1b",
        "t5gemma2-4b",
        "qwen3-4b",
        "qwen3-1.7b",
    }


def test_format_kind_per_family() -> None:
    assert model_format_kind("gemma4-e4b") == "chat"
    assert model_format_kind("qwen3-4b") == "chat"
    assert model_format_kind("t5gemma2-1b") == "seq2seq"


def test_unknown_key_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported model key"):
        get_model_spec("nope")


def test_require_hf_id_returns_wired_id() -> None:
    assert require_hf_id("gemma4-e4b") == "unsloth/gemma-4-E4B-it-unsloth-bnb-4bit"
    assert require_hf_id("t5gemma2-270m") == "google/t5gemma-2-270m-270m"
    assert require_hf_id("t5gemma2-1b") == "google/t5gemma-2-1b-1b"


def test_require_hf_id_raises_for_formatting_only_keys() -> None:
    # qwen3 keys can be formatted but not trained until their repo ids are confirmed.
    for key in ("qwen3-4b", "qwen3-1.7b"):
        with pytest.raises(ValueError, match="no HF id"):
            require_hf_id(key)
