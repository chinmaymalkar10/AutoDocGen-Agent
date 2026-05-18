import re
from pathlib import Path
from state import DocState
from utils.llm import call_llm

PACKAGE_FILES = {
    "requirements.txt", "requirements-dev.txt", "requirements_dev.txt",
    "setup.py", "setup.cfg", "pyproject.toml",
    "package.json", "package-lock.json",
    "Cargo.toml", "go.mod", "go.sum",
    "Gemfile", "Gemfile.lock",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "composer.json",
}


def _parse_requirements_txt(content: str) -> list[str]:
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            name = re.split(r"[>=<!~\[]", line)[0].strip()
            if name:
                deps.append(line)
    return deps


def _parse_package_json(content: str) -> tuple[list[str], list[str]]:
    import json
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return [], []
    deps = [f"{k}@{v}" for k, v in data.get("dependencies", {}).items()]
    dev = [f"{k}@{v}" for k, v in data.get("devDependencies", {}).items()]
    return deps, dev


def _parse_generic(content: str) -> list[str]:
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    return lines[:100]


def dependency_analyzer(state: DocState) -> dict:
    repo_path = Path(state["repo_path"])
    dependencies: dict[str, list[str]] = {}
    dev_dependencies: dict[str, list[str]] = {}

    for pkg_file in PACKAGE_FILES:
        path = repo_path / pkg_file
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if pkg_file == "package.json":
            deps, devs = _parse_package_json(content)
            if deps:
                dependencies[pkg_file] = deps
            if devs:
                dev_dependencies[pkg_file] = devs
        elif "requirements" in pkg_file:
            deps = _parse_requirements_txt(content)
            if deps:
                dependencies[pkg_file] = deps
        else:
            deps = _parse_generic(content)
            if deps:
                dependencies[pkg_file] = deps

    all_deps = []
    for fname, deps in {**dependencies, **dev_dependencies}.items():
        all_deps.append(f"=== {fname} ===\n" + "\n".join(deps))

    dep_summary = ""
    if all_deps:
        dep_summary = call_llm(
            "You are a software dependency expert. Categorize the dependencies (core, dev, testing, database, web framework, etc.) and briefly explain what the key ones do.",
            "\n\n".join(all_deps),
            max_tokens=1500,
            caller="Dependency Analyzer",
        )

    return {
        "dependencies": dependencies,
        "dev_dependencies": dev_dependencies,
        "dependency_summary": dep_summary,
    }
