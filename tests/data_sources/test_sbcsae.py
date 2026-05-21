from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from scripttuner.data_sources import sbcsae


def _make_fake_zip(n_files: int = 60, *, include_noise: bool = True) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("SBCSAE/", "")
        for i in range(1, n_files + 1):
            zf.writestr(
                f"SBCSAE/SBC{i:03d}.cha",
                f"@UTF8\n@Begin\n*A: line {i}\n@End\n",
            )
        if include_noise:
            zf.writestr("__MACOSX/SBCSAE/._SBC001.cha", "noise")
            zf.writestr("SBCSAE/0metadata.cdc", "metadata noise")
    return buf.getvalue()


def test_download_extracts_60_cha_files(tmp_path: Path) -> None:
    fake_zip = _make_fake_zip()
    files = sbcsae.download(tmp_path, fetcher=lambda _url: fake_zip)
    assert len(files) == 60
    assert all(f.name.startswith("SBC") and f.suffix == ".cha" for f in files)
    assert all(f.parent == tmp_path for f in files)


def test_download_is_idempotent(tmp_path: Path) -> None:
    fake_zip = _make_fake_zip()
    calls = {"n": 0}

    def fetcher(_url: str) -> bytes:
        calls["n"] += 1
        return fake_zip

    sbcsae.download(tmp_path, fetcher=fetcher)
    sbcsae.download(tmp_path, fetcher=fetcher)
    assert calls["n"] == 1


def test_download_force_redownloads(tmp_path: Path) -> None:
    fake_zip = _make_fake_zip()
    calls = {"n": 0}

    def fetcher(_url: str) -> bytes:
        calls["n"] += 1
        return fake_zip

    sbcsae.download(tmp_path, fetcher=fetcher)
    sbcsae.download(tmp_path, force=True, fetcher=fetcher)
    assert calls["n"] == 2


def test_download_excludes_noise(tmp_path: Path) -> None:
    fake_zip = _make_fake_zip(include_noise=True)
    files = sbcsae.download(tmp_path, fetcher=lambda _url: fake_zip)
    assert not any("MACOSX" in str(f) for f in files)
    assert not any(f.name == "0metadata.cdc" for f in files)


def test_download_raises_on_wrong_count(tmp_path: Path) -> None:
    fake_zip = _make_fake_zip(n_files=59, include_noise=False)
    with pytest.raises(RuntimeError, match="Expected 60"):
        sbcsae.download(tmp_path, fetcher=lambda _url: fake_zip)
