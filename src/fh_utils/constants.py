from pathlib import Path

CACHE_DIR = Path.home() / ".cache/fasthtml"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
