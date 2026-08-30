#!/usr/bin/env python3
"""Add a project card to projects.html for any public repo not already listed.

Run by .github/workflows/sync-projects.yml. Safe to run manually too:
    python3 scripts/sync_projects.py
"""
import json
import re
import urllib.request
from pathlib import Path

USERNAME = "codemastervy"
SKIP_REPOS = {"codemastervy", "codemastervy.github.io"}
PROJECTS_FILE = Path(__file__).resolve().parent.parent / "projects.html"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

GRID_CLOSE = "        </div>\n      </div>\n    </section>"


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=created",
        headers={"Accept": "application/vnd.github+json", "User-Agent": USERNAME},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def existing_repo_names(html):
    return set(re.findall(rf'github\.com/{USERNAME}/([\w.-]+)"', html))


def format_date(created_at):
    year, month = created_at[:4], int(created_at[5:7])
    return f"{MONTHS[month - 1]} {year} to Present"


def title_case(name):
    return re.sub(r"[-_]+", " ", name).title()


def build_card(repo):
    name = repo["name"]
    title = title_case(name)
    desc = repo["description"] or f"See the {name} repository on GitHub for details."
    date = format_date(repo["created_at"])
    tags = repo.get("topics") or ([repo["language"]] if repo.get("language") else [])
    tags = tags[:3] or ["Project"]
    chips = "".join(
        f'<span class="chip">{title_case(t)}</span>' for t in tags
    )
    return (
        f'          <div class="project-card">\n'
        f'            <div class="project-thumb"></div>\n'
        f'            <h4>{title}</h4>\n'
        f'            <div class="project-date">{date}</div>\n'
        f'            <p>{desc}</p>\n'
        f'            <div class="chip-row">{chips}</div>\n'
        f'            <a class="repo-link" href="https://github.com/{USERNAME}/{name}" '
        f'target="_blank" rel="noopener">View on GitHub →</a>\n'
        f'          </div>\n'
    )


def bump_everything_count(html):
    count = html.count('<div class="project-card">')
    return re.sub(
        r'(<button class="filter-btn active">Everything )\d+(</button>)',
        rf"\g<1>{count}\g<2>",
        html,
        count=1,
    )


def main():
    html = PROJECTS_FILE.read_text(encoding="utf-8")
    known = existing_repo_names(html)

    repos = fetch_repos()
    new_repos = [
        r for r in repos
        if not r["fork"] and r["name"] not in SKIP_REPOS and r["name"] not in known
    ]

    if not new_repos:
        print("No new repos to add.")
        return

    cards = "".join(build_card(r) for r in new_repos)
    if GRID_CLOSE not in html:
        raise SystemExit("Could not find the project-grid closing anchor. "
                          "projects.html structure may have changed — update GRID_CLOSE.")
    html = html.replace(GRID_CLOSE, cards + GRID_CLOSE, 1)
    html = bump_everything_count(html)

    PROJECTS_FILE.write_text(html, encoding="utf-8")
    names = ", ".join(r["name"] for r in new_repos)
    print(f"Added {len(new_repos)} project card(s): {names}")


if __name__ == "__main__":
    main()
