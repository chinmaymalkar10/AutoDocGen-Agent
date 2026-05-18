import os
import re
import shutil
import stat
from pathlib import Path
from git import Repo

PROJECT_DIR = Path(__file__).resolve().parent.parent
CLONE_DIR = PROJECT_DIR / "cloned_repo"


def _force_remove_readonly(func, path, _exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def is_github_url(input_str: str) -> bool:
    return bool(re.match(r"https?://(www\.)?github\.com/.+/.+", input_str.strip()))


def load_repo(input_str: str) -> tuple[str, str | None]:
    """Returns (local_path, original_url_or_None)."""
    input_str = input_str.strip()
    if is_github_url(input_str):
        cleanup_cloned_repo()
        CLONE_DIR.mkdir(exist_ok=True)
        Repo.clone_from(input_str, str(CLONE_DIR), depth=1)
        return str(CLONE_DIR), input_str

    path = Path(input_str)
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {input_str}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {input_str}")
    return str(path.resolve()), None


def cleanup_cloned_repo():
    if CLONE_DIR.exists():
        shutil.rmtree(CLONE_DIR, onerror=_force_remove_readonly)
