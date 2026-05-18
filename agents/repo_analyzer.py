from state import DocState
from utils.file_utils import (
    walk_repo, build_file_tree, detect_languages,
    detect_frameworks, count_lines, find_existing_docs,
)
import config


def repo_analyzer(state: DocState) -> dict:
    repo_path = state["repo_path"]
    files = walk_repo(repo_path)
    total_lines = count_lines(files)

    return {
        "file_tree": build_file_tree(repo_path, files),
        "languages": detect_languages(files),
        "frameworks": detect_frameworks(repo_path, files),
        "existing_docs": find_existing_docs(repo_path),
        "total_lines": total_lines,
        "is_large_repo": total_lines > config.LARGE_REPO_THRESHOLD,
    }
