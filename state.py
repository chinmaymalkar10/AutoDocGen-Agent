from typing import TypedDict, Optional


class DocState(TypedDict):
    repo_path: str
    repo_url: Optional[str]

    file_tree: str
    languages: list[str]
    frameworks: list[str]
    existing_docs: dict[str, str]
    total_lines: int
    is_large_repo: bool

    entry_points: list[dict]
    config_summaries: list[dict]
    module_summaries: list[dict]

    dependencies: dict[str, list[str]]
    dev_dependencies: dict[str, list[str]]
    dependency_summary: str

    final_markdown: str
