#!/usr/bin/env python3
"""Remove all non-YouTube cookies from a Netscape format cookies file."""

import sys
from pathlib import Path


def clean_cookies(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    with open(path, "r") as f:
        lines = f.readlines()

    header = (
        lines[0]
        if lines and lines[0].startswith("# Netscape HTTP Cookie File")
        else "# Netscape HTTP Cookie File\n"
    )

    kept = [header]
    removed = 0

    for line in lines[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split("\t")
        if len(fields) >= 1 and "youtube" in fields[0].lower():
            kept.append(line)
        else:
            removed += 1

    with open(path, "w") as f:
        f.writelines(kept)

    print(f"Kept {len(kept) - 1} youtube cookie lines")
    print(f"Removed {removed} non-youtube lines")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <cookies_file>")
        sys.exit(1)

    clean_cookies(sys.argv[1])
