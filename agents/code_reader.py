from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from state import DocState
from utils.file_utils import (
    walk_repo, find_entry_points, find_config_files, read_file_content,
)
from utils.llm import call_llm
import config

SYSTEM_PROMPT = (
    "You are a code documentation expert. Given a source file, provide a concise summary with:\n"
    "- File purpose (1 sentence)\n"
    "- Key classes/functions and what they do\n"
    "- Public API or exports\n"
    "- Notable patterns or dependencies\n"
    "Keep it to 3-5 bullet points."
)


def _summarize_file(path: Path, repo_path: str) -> dict:
    rel = str(path.relative_to(repo_path))
    content = read_file_content(path)
    if not content.strip():
        return {"path": rel, "summary": "Empty file"}

    summary = call_llm(
        SYSTEM_PROMPT,
        f"File: {rel}\n\n```\n{content}\n```",
        max_tokens=config.MAX_TOKENS,
        caller=f"Code Reader ({rel})",
    )
    return {"path": rel, "summary": summary}


def _get_top_modules(files: list[Path], exclude: set[Path], limit: int) -> list[Path]:
    candidates = [f for f in files if f not in exclude and f.suffix in (".py", ".js", ".ts", ".tsx", ".go", ".rs", ".java", ".rb")]
    sized = []
    for f in candidates:
        try:
            sized.append((f, f.stat().st_size))
        except OSError:
            continue
    sized.sort(key=lambda x: x[1], reverse=True)
    return [f for f, _ in sized[:limit]]


def _summarize_batch(file_list: list[Path], repo_path: str) -> list[dict]:
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(_summarize_file, f, repo_path): f for f in file_list}
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    return results


def code_reader_full(state: DocState) -> dict:
    repo_path = state["repo_path"]
    files = walk_repo(repo_path)
    entries = find_entry_points(repo_path, files)
    configs = find_config_files(files)
    exclude = set(entries) | set(configs)
    modules = _get_top_modules(files, exclude, config.MAX_FILES_FULL - len(entries) - len(configs))

    return {
        "entry_points": _summarize_batch(entries, repo_path),
        "config_summaries": _summarize_batch(configs, repo_path),
        "module_summaries": _summarize_batch(modules, repo_path),
    }


def code_reader_chunked(state: DocState) -> dict:
    repo_path = state["repo_path"]
    files = walk_repo(repo_path)
    entries = find_entry_points(repo_path, files)[:5]
    configs = find_config_files(files)[:5]
    exclude = set(entries) | set(configs)
    modules = _get_top_modules(files, exclude, 10)

    return {
        "entry_points": _summarize_batch(entries, repo_path),
        "config_summaries": _summarize_batch(configs, repo_path),
        "module_summaries": _summarize_batch(modules, repo_path),
    }
