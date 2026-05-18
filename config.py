import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
API_VERSION = os.getenv("API_VERSION")
MODEL = os.getenv("MODEL", "gpt-5.2")

ENABLE_LOGGING = True
JSON_LOG_FILE = Path(__file__).resolve().parent / "logs.jsonl"
ERROR_LOG_FILE = Path(__file__).resolve().parent / "errors.jsonl"

MAX_TOKENS = 2000
DOC_GEN_MAX_TOKENS = 6000
LARGE_REPO_THRESHOLD = 50000
MAX_FILE_LINES = 500
TRUNCATE_HEAD = 200
TRUNCATE_TAIL = 50
MAX_FILES_FULL = 30
MAX_FILES_CHUNKED = 15

SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", ".tox",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs",
    "env", ".env", ".idea", ".vscode", "target", "bin", "obj",
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".pyc", ".pyo", ".class", ".jar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".sqlite", ".db",
}
