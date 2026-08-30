# Portfolio Sync Action

A GitHub Actions workflow that watches your public repos and automatically
adds any new one to a portfolio site's Projects page and your GitHub profile
README — no manual editing required after uploading a new repo.

It runs on a daily schedule and can also be triggered manually from the
Actions tab.

Extracted from [codemastervy.github.io](https://github.com/codemastervy/codemastervy.github.io)
and [codemastervy](https://github.com/codemastervy/codemastervy), where it's used
in production. This repo is the documented reference copy — drop the matching
script and workflow into another repo to adopt it there.

---

## What it does

```
schedule (daily, or run manually)
        │
        ▼
  list all public repos for the account (GitHub REST API, no auth needed)
        │
        ▼
  drop forks, drop the repo running this workflow, drop repos already
  listed in the target file
        │
        │ anything left over?
        ▼
  build a card / table row from each repo's name, description,
  creation date, topics (or primary language)
        │
        ▼
  insert it into the target file, commit as github-actions[bot], push
```

If nothing new is found, it exits without committing — no empty commits,
no noise in the history.

---

## Two scripts, two destinations

| Script | Destination | Format |
|---|---|---|
| `scripts/sync_projects.py` | A portfolio site's `projects.html` | Inserts a `.project-card` HTML block before the closing tags of `.project-grid`, and bumps the "Everything N" filter count |
| `scripts/sync_readme.py` | A GitHub profile README's `README.md` | Inserts a Markdown table row into the Repositories table, after the last *linked* row (so a placeholder "coming soon" row stays at the bottom) |

Both scripts are stdlib-only Python (`urllib`, `re`, `json`) — nothing to
`pip install`, nothing to configure beyond the two constants at the top of
each file.

---

## Setup (per repo you want this in)

### 1. Copy the files in

```bash
cp scripts/sync_projects.py     <target-repo>/scripts/       # for an HTML portfolio
# or
cp scripts/sync_readme.py       <target-repo>/scripts/       # for a profile README

cp .github/workflows/sync-projects.yml   <target-repo>/.github/workflows/
# or
cp .github/workflows/sync-readme.yml     <target-repo>/.github/workflows/
```

### 2. Edit the two constants at the top of the script

```python
USERNAME = "your-github-username"
SKIP_REPOS = {"your-username", "your-username.github.io"}  # repos to never add a card/row for
```

### 3. Adjust the anchor if your file structure differs

- `sync_projects.py` looks for a specific closing-tag sequence (`GRID_CLOSE`)
  to know where to insert new cards. If your `projects.html` doesn't share
  the same `.project-grid` / `.card` / `.panel` nesting, update that
  constant to match.
- `sync_readme.py` looks for the last Markdown table row starting with
  `| **[` that contains a `github.com/<username>/` link. If your README's
  table looks different, adjust the matching logic in `main()`.

### 4. Commit and push

No secrets to configure — each workflow uses that repo's own built-in
`GITHUB_TOKEN` (declared with `permissions: contents: write` in the
workflow file) to commit back to itself. It never needs to reach into a
different repo, so there's no cross-repo token to manage.

---

## Why it only touches public, non-fork repos

The GitHub API endpoint used (`GET /users/{username}/repos`) only ever
returns public repositories, and the scripts explicitly skip anything with
`"fork": true`. That means forked repos (tools you use but didn't build)
never show up as if they were your own work, and private repos are never
exposed on a public portfolio by accident.

## Why commits are attributed to `github-actions[bot]`, not you

These are automated edits, not something typed on a given day. Attributing
them to a bot keeps a GitHub contribution graph honest — it reflects what
was actually written by hand versus what a scheduled job did on your behalf.
If you'd rather these commits count as yours, change the `git config
user.name` / `user.email` lines in the workflow file's last step.

## License

[MIT](LICENSE) — take it, adapt it for your own site.
