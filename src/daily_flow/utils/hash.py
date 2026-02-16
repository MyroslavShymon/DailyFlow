import hashlib
from pathlib import Path
from typing import Union

def calculate_file_hash(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Can't hash a non-existent file: {file_path}")

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest()