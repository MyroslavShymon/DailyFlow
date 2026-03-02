import argparse
import sys
from pathlib import Path

from scripts.backup.apply_retention import apply_retention
from scripts.backup.create_backup import create_backup
from scripts.backup.write_manifest import write_manifest


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    Path(args.out).mkdir(parents=True, exist_ok=True)

    result = create_backup(args.db, args.out)

    write_manifest(result, args.out)

    if result.status == "success":
        apply_retention(args.out)

    if result.status != "success":
        print(f"Backup FAILED: {result.error_message}")
        sys.exit(1)

    print(f"Backup OK: {Path(args.out) / result.file_name}")
    sys.exit(0)


if __name__ == "__main__":
    main()
