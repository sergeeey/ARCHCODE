#!/usr/bin/env python3
"""
Lightweight secret scan for tracked text files.
Fails with non-zero exit code if suspicious patterns are found.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z\-_]{35}",
    r"ghp_[0-9A-Za-z]{36}",
    r"xox[baprs]-[0-9A-Za-z-]{10,}",
    r"BEGIN (?:RSA|EC|DSA|OPENSSH|PRIVATE) KEY",
]

TEXT_EXTS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".env",
    ".txt",
    ".cjs",
}


def tracked_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    files = []
    for line in out.splitlines():
        p = Path(line)
        if p.suffix.lower() in TEXT_EXTS and p.is_file():
            files.append(p)
    return files


def main() -> int:
    regexes = [re.compile(p) for p in PATTERNS]
    hits: list[str] = []

    for file in tracked_files():
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rx in regexes:
            for m in rx.finditer(content):
                hits.append(f"{file}:{m.start()} pattern={rx.pattern}")

    if hits:
        print("Secret scan FAILED. Suspicious patterns found:")
        for h in hits[:50]:
            print(f"- {h}")
        if len(hits) > 50:
            print(f"... and {len(hits) - 50} more")
        return 1

    print("Secret scan PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

