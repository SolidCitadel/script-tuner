"""Push a trained LoRA adapter to the HuggingFace Hub.

Uploads the adapter folder that already exists on disk
(`runs/finetune/<run-name>/adapter/`) — it does NOT reload the gated base
model, so it is fast and needs no extra download.

License note: SBCSAE is CC BY-ND 3.0 US (No Derivatives). A LoRA adapter trained
on it is a derivative work, so the target repo defaults to **private**. Do not
flip to public without resolving the license question.

Usage:
    uv run python scripts/push_adapter.py \
        --run-name t5gemma2-1b-SBCSAE-lora-es \
        --repo-id SolidCitadel/scripttuner-t5gemma2-1b-sbcsae-casual

    # public (only if the license allows — it currently does not):
    uv run python scripts/push_adapter.py ... --public
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import dotenv
from huggingface_hub import HfApi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-name",
        required=True,
        help="Finetune run name under runs/finetune/ (its adapter/ subdir is uploaded).",
    )
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Target HF repo, e.g. SolidCitadel/scripttuner-t5gemma2-1b-sbcsae-casual",
    )
    parser.add_argument(
        "--runs-dir",
        default="runs/finetune",
        help="Base directory holding finetune runs (default: runs/finetune).",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Create a PUBLIC repo. Off by default — SBCSAE CC BY-ND forbids it.",
    )
    args = parser.parse_args()

    dotenv.load_dotenv()
    token = os.environ.get("HF_TOKEN")
    if not token:
        parser.error("HF_TOKEN not found (set it in .env or the environment).")

    adapter_dir = Path(args.runs_dir) / args.run_name / "adapter"
    if not adapter_dir.is_dir():
        parser.error(f"adapter dir not found: {adapter_dir}")

    api = HfApi(token=token)
    api.create_repo(args.repo_id, private=not args.public, exist_ok=True)
    visibility = "PUBLIC" if args.public else "private"
    print(f"Uploading {adapter_dir} -> {args.repo_id} ({visibility}) ...")
    api.upload_folder(
        repo_id=args.repo_id,
        folder_path=str(adapter_dir),
        commit_message=f"Upload adapter from run {args.run_name}",
    )
    print(f"Done: https://huggingface.co/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())