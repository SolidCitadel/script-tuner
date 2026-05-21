"""ScriptTuner CLI 진입점.

사용 예:
    uv run scripttuner download sbcsae
    uv run scripttuner download sbcsae --force
    uv run scripttuner --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import ModuleType

from scripttuner.data_sources import sbcsae

DEFAULT_DATASETS_DIR = Path("datasets")
CORPORA: dict[str, ModuleType] = {"sbcsae": sbcsae}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scripttuner", description="ScriptTuner CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dl = subparsers.add_parser("download", help="Download a dataset by name.")
    dl.add_argument("corpus", choices=sorted(CORPORA), help="Corpus to download.")
    dl.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DATASETS_DIR,
        help=f"Base destination directory (default: {DEFAULT_DATASETS_DIR}).",
    )
    dl.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if files already exist.",
    )

    return parser


def _run_download(args: argparse.Namespace) -> int:
    module = CORPORA[args.corpus]
    dest_dir = args.dest / args.corpus
    files = module.download(dest_dir, force=args.force)
    print(f"OK: {len(files)} files in {dest_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "download":
        return _run_download(args)
    parser.error(f"Unknown command: {args.command}")
    return 2  # unreachable; parser.error exits


if __name__ == "__main__":
    sys.exit(main())
