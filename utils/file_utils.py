from pathlib import Path
from collections import Counter
import config

LANG_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript (React)", ".jsx": "JavaScript (React)",
    ".java": "Java", ".kt": "Kotlin", ".go": "Go",
    ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".cs": "C#", ".cpp": "C++", ".c": "C", ".h": "C/C++ Header",
    ".swift": "Swift", ".scala": "Scala", ".r": "R", ".R": "R",
    ".sql": "SQL", ".sh": "Shell", ".bash": "Shell",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".yaml": "YAML", ".yml": "YAML", ".json": "JSON",
    ".xml": "XML", ".toml": "TOML", ".md": "Markdown",
}

FRAMEWORK_SIGNATURES = {
    "manage.py": "Django",
    "django": "Django",
    "next.config.js": "Next.js",
    "next.config.mjs": "Next.js",
    "next.config.ts": "Next.js",
    "nuxt.config.ts": "Nuxt.js",
    "angular.json": "Angular",
    "vue.config.js": "Vue.js",
    "svelte.config.js": "SvelteKit",
    "Cargo.toml": "Rust/Cargo",
    "go.mod": "Go Modules",
    "build.gradle": "Gradle",
    "pom.xml": "Maven",
    "Gemfile": "Ruby/Bundler",
    "composer.json": "PHP/Composer",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "serverless.yml": "Serverless Framework",
    "terraform": "Terraform",
    "setup.py": "Python Setuptools",
    "pyproject.toml": "Python (pyproject)",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "streamlit": "Streamlit",
    "express": "Express.js",
    "spring": "Spring",
}


def should_skip(path: Path) -> bool:
    return any(part in config.SKIP_DIRS for part in path.parts)


def is_binary(path: Path) -> bool:
    return path.suffix.lower() in config.BINARY_EXTENSIONS


def walk_repo(repo_path: str) -> list[Path]:
    root = Path(repo_path)
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not should_skip(p) and not is_binary(p):
            files.append(p)
    return sorted(files)


def build_file_tree(repo_path: str, files: list[Path]) -> str:
    root = Path(repo_path)
    lines = []
    for f in files:
        rel = f.relative_to(root)
        depth = len(rel.parts) - 1
        lines.append("  " * depth + rel.name)
    return "\n".join(lines[:500])


def detect_languages(files: list[Path]) -> list[str]:
    counts = Counter()
    for f in files:
        lang = LANG_MAP.get(f.suffix.lower())
        if lang:
            counts[lang] += 1
    return [lang for lang, _ in counts.most_common(10)]


def detect_frameworks(repo_path: str, files: list[Path]) -> list[str]:
    found = set()
    filenames = {f.name for f in files}
    for sig, framework in FRAMEWORK_SIGNATURES.items():
        if sig in filenames:
            found.add(framework)

    for f in files:
        if f.suffix.lower() in (".py", ".js", ".ts"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:2000]
                for keyword, framework in FRAMEWORK_SIGNATURES.items():
                    if keyword in content.lower():
                        found.add(framework)
            except OSError:
                continue
    return sorted(found)


def count_lines(files: list[Path]) -> int:
    total = 0
    for f in files:
        try:
            total += sum(1 for _ in f.open(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return total


def read_file_content(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""

    if len(lines) <= config.MAX_FILE_LINES:
        return "\n".join(lines)

    head = lines[: config.TRUNCATE_HEAD]
    tail = lines[-config.TRUNCATE_TAIL :]
    return "\n".join(head) + f"\n\n... [{len(lines) - config.TRUNCATE_HEAD - config.TRUNCATE_TAIL} lines truncated] ...\n\n" + "\n".join(tail)


def find_existing_docs(repo_path: str) -> dict[str, str]:
    root = Path(repo_path)
    docs = {}
    doc_patterns = ["README*", "CONTRIBUTING*", "CHANGELOG*", "LICENSE*", "INSTALL*", "SETUP*"]
    for pattern in doc_patterns:
        for f in root.glob(pattern):
            if f.is_file():
                try:
                    docs[f.name] = f.read_text(encoding="utf-8", errors="ignore")[:5000]
                except OSError:
                    continue

    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for f in docs_dir.rglob("*.md"):
            if f.is_file() and not should_skip(f):
                try:
                    rel = str(f.relative_to(root))
                    docs[rel] = f.read_text(encoding="utf-8", errors="ignore")[:3000]
                except OSError:
                    continue
    return docs


def find_entry_points(repo_path: str, files: list[Path]) -> list[Path]:
    entry_names = {"main", "app", "index", "__main__", "server", "cli", "run", "manage"}
    entries = []
    for f in files:
        stem = f.stem.lower()
        if stem in entry_names:
            entries.append(f)
            continue
        if f.suffix == ".py":
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:3000]
                if 'if __name__' in content:
                    entries.append(f)
            except OSError:
                continue
    return entries


def find_config_files(files: list[Path]) -> list[Path]:
    config_names = {"config", "settings", "constants", "conf"}
    config_patterns = {".env.example", ".env.sample", "Makefile", "Procfile"}
    configs = []
    for f in files:
        stem = f.stem.lower()
        if stem in config_names or f.name in config_patterns:
            configs.append(f)
        elif ".config." in f.name.lower():
            configs.append(f)
    return configs
