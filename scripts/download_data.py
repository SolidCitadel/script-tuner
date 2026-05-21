"""Download a dataset by name into ./datasets/<corpus>/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripttuner.data_sources import sbcsae

DEFAULT_DEST = Path("datasets")
CORPORA = {"sbcsae": sbcsae}


def main() -> int:
    parser = argparse.ArgumentParser(description="Download a dataset by name.")
    parser.add_argument("corpus", choices=sorted(CORPORA), help="Corpus to download.")
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help=f"Base destination directory (default: {DEFAULT_DEST}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if files already exist.",
    )
    args = parser.parse_args()

    module = CORPORA[args.corpus]
    dest_dir = args.dest / args.corpus
    files = module.download(dest_dir, force=args.force)
    print(f"OK: {len(files)} files in {dest_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
