import json
from dataclasses import asdict
from pathlib import Path

from scripts.backup.create_backup import BackupResult


def write_manifest(
    backup_data: BackupResult, out_dir: str, manifest_file_name: str = "manifest.jsonl"
):
    manifest_file = Path(out_dir) / manifest_file_name

    with open(manifest_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(backup_data), ensure_ascii=False) + "\n")
