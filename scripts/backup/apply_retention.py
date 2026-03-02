from pathlib import Path


def apply_retention(backups_dir: str, policy="last_n", n=3):
    all_backups = sorted(
        [f for f in Path(backups_dir).glob("dailyflow_*.sqlite3.gz")],
        key=lambda f: f.name,
        reverse=True,
    )

    if policy == "last_n":
        for old_file in all_backups[n:]:
            old_file.unlink()
            print(f"Deleted old backup: {old_file.name}")
