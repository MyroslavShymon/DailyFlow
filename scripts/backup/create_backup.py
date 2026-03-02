import datetime
import gzip
import os
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from .utils import calculate_file_hash

BackupStatus = Literal["success", "fail"]
IntegrityCheck = Literal["ok", "fail"]


@dataclass(frozen=True)
class BackupResult:
    status: BackupStatus
    integrity_check: IntegrityCheck
    file_name: str
    db_path: str
    created_at: str

    error_message: str | None = None

    file_hash: str | None = None
    file_size: int | None = None


def create_backup(db_path: str, out_dir: str) -> BackupResult:
    tmp_path: str | None = None

    current_datetime = datetime.datetime.now(tz=datetime.UTC)
    created_at = current_datetime.strftime("%Y-%m-%d_%H-%M")

    backup_filename = f"dailyflow_{created_at}.sqlite3.gz"

    backup_default_result = BackupResult(
        status="success",
        created_at=created_at,
        integrity_check="ok",
        db_path=db_path,
        file_name=backup_filename,
    )

    try:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name

        with sqlite3.connect(db_path) as src_conn, sqlite3.connect(tmp_path) as dst_conn:
            src_conn.backup(dst_conn)

        check_conn = sqlite3.connect(tmp_path)
        [integrity_check] = check_conn.execute("PRAGMA integrity_check;").fetchone()
        check_conn.close()

        integrity_check: IntegrityCheck = "ok" if integrity_check == "ok" else "fail"

        if integrity_check != "ok":
            integrity_check_error = f"CRITICAL: Integrity check failed for {db_path}"
            print(integrity_check_error)
            return replace(
                backup_default_result,
                integrity_check=integrity_check,
                error_message=integrity_check_error,
                status="fail",
            )

        full_path = Path(out_dir) / backup_filename

        with open(full_path, "wb") as f_raw:
            # mtime=0 робить хеш файлу стабільним, якщо вміст БД не змінився
            with gzip.GzipFile(fileobj=f_raw, mode="wb", mtime=0, compresslevel=9) as f_out:
                with open(tmp_path, "rb") as f_in:
                    shutil.copyfileobj(
                        f_in, f_out
                    )  # Ефективніше за f_out.write(f_in.read()), пише потроху

        file_size_bytes = os.path.getsize(full_path)

        file_hash = calculate_file_hash(full_path)

        return replace(backup_default_result, file_hash=file_hash, file_size=file_size_bytes)
    except sqlite3.Error as e:
        print(f"Database error during backup: {e}")
        return replace(
            backup_default_result,
            status="fail",
            error_message=repr(e),
        )
    except OSError as e:
        print(f"File system error: {e}")
        return replace(
            backup_default_result,
            status="fail",
            error_message=repr(e),
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        return replace(
            backup_default_result,
            status="fail",
            error_message=repr(e),
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
