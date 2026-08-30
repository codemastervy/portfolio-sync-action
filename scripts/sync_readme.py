#!/usr/bin/env python3
"""Add a row to the Repositories table in README.md for any public repo not
already listed.

Run by .github/workflows/sync-readme.yml. Safe to run manually too:
    python3 scripts/sync_readme.py
"""
import json
import re
import urllib.request
from pathlib import Path

USERNAME = "codemastervy"
SKIP_REPOS = {"codemastervy", "codemastervy.github.io"}
README_FILE = Path(__file__).resolve().parent.parent / "README.md"


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=created",
        headers={"Accept": "application/vnd.github+json", "User-Agent": USERNAME},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def existing_repo_names(md):
    return set(re.findall(rf'github\.com/{USERNAME}/([\w.-]+)\)', md))


def build_row(repo):
    name = repo["name"]
    desc = repo["description"] or "See the repo for details."
    return f"| **[{name}](https://github.com/{USERNAME}/{name})** | {desc} |\n"


def main():
    md = README_FILE.read_text(encoding="utf-8")
    known = existing_repo_names(md)

    repos = fetch_repos()
    new_repos = [
        r for r in repos
        if not r["fork"] and r["name"] not in SKIP_REPOS and r["name"] not in known
    ]

    if not new_repos:
        print("No new repos to add.")
        return

    # Insert after the last *linked* repo row, so a placeholder row with no
    # link yet (e.g. "repo coming soon") stays at the bottom of the table.
    lines = md.splitlines(keepends=True)
    last_row = None
    for i, line in enumerate(lines):
        if line.startswith("| **[") and f"github.com/{USERNAME}/" in line:
            last_row = i
    if last_row is None:
        raise SystemExit("Could not find the Repositories table in README.md.")

    new_rows = [build_row(r) for r in new_repos]
    lines[last_row + 1:last_row + 1] = new_rows
    README_FILE.write_text("".join(lines), encoding="utf-8")

    names = ", ".join(r["name"] for r in new_repos)
    print(f"Added {len(new_repos)} repo row(s): {names}")


if __name__ == "__main__":
    main()
