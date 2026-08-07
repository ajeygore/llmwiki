# LLMWiki Engine Upgrade Instruction Manual for AI Agents

You are an AI coding assistant helping the user upgrade the LLMWiki **engine** (the `llmwiki/` folder) inside an **already-bootstrapped** wiki workspace to the latest version from `https://github.com/ajeygore/llmwiki`. This manual is for existing wikis. If `llmwiki/`, `agents.md`, or `wiki/` don't exist yet, this is a new setup instead — read `setup.md` at `https://raw.githubusercontent.com/ajeygore/llmwiki/main/setup.md`.

**Never modify anything under `/wiki/` or `/raw/` as part of an engine upgrade.** This is purely about refreshing the rendering engine and, optionally, reconciling root-level templates it originally generated.

## 1. Check for a Clean Working Tree
Before touching anything, run `git status`. If there are uncommitted changes, stop and ask the user to commit or stash them first — an engine upgrade should be its own isolated, revertible commit.

## 2. Detect How the Engine Was Added
```bash
git config --file .gitmodules --get-regexp path 2>/dev/null | grep llmwiki
```
- **Match found (or a `.gitmodules` entry for `llmwiki`)** → it's a **submodule**. Go to 3A.
- **No match** → it's **vendored** (a plain committed copy). Go to 3B.

## 3A. Update a Submodule
```bash
git submodule update --remote --merge
```
This fetches and merges upstream engine changes into the linked `llmwiki/` checkout. Resolve any merge conflicts inside `llmwiki/` in favor of upstream (the folder should never carry local edits — see `agents.md`'s rule that agents never modify files inside `/llmwiki/`).

## 3B. Update a Vendored Copy
Replace the folder wholesale with a fresh shallow clone, same as the original install:
```bash
rm -rf llmwiki
git clone --depth 1 https://github.com/ajeygore/llmwiki.git llmwiki
rm -rf llmwiki/.git
```

## 4. Reconcile Root-Level Templates (Important)
`setup.py`/`setup.sh`/`setup.bat` only **create files that are missing** — they never overwrite `index.html`, `agents.md`, `README.md`, or the `wiki/*.md` skeleton pages once they exist. That means engine upgrades that change those templates (a new header button, a new agent rule, a new page layout) do **not** reach an existing wiki automatically. After step 3, check whether this upgrade needs any of that:

1. Skim recent commits on the upstream engine (`git -C llmwiki log --oneline -20` if it's a submodule, or browse `https://github.com/ajeygore/llmwiki/commits/main/setup.py` otherwise) for anything that touches `setup.py`'s `index_html_content`, `agents_md_content`, or the `wiki/` skeleton strings.
2. If it does, generate a fresh set of templates in a **scratch empty directory** to diff against the real ones:
   ```bash
   mkdir -p /tmp/llmwiki-upgrade-check && cd /tmp/llmwiki-upgrade-check
   python3 <path-to-workspace>/llmwiki/setup.py --name "<current wiki name>"
   diff /tmp/llmwiki-upgrade-check/index.html <path-to-workspace>/index.html
   diff /tmp/llmwiki-upgrade-check/agents.md <path-to-workspace>/agents.md
   ```
3. Manually merge in only the relevant new pieces the diff surfaces (e.g. a new button's markup in `index.html`, a new rule in `agents.md`). Preserve the user's existing customizations (wiki name, custom styling, added rules) — this is a targeted merge, not an overwrite.
4. If nothing in this upgrade touches those templates, skip this step — most engine updates (JS/CSS fixes, new engine features that read existing markup) need no template changes at all.

## 5. Verify
```bash
./llmwiki/lint
./llmwiki/run
```
Open the dashboard and spot-check: the sidebar loads, a few pages render, and (if step 4 applied) the new feature actually shows up.

## 6. Log, Commit, and Push
Follow the same discipline as any other major change (see `agents.md` → "Reprocess After Every Major Task"):
1. Append an entry to `wiki/log.md` in the parseable format: `## [YYYY-MM-DD] update-engine | Upgraded LLMWiki engine to latest (<vendored|submodule>)<, reconciled index.html/agents.md if applicable>`.
2. `./llmwiki/lint && git add -A && git commit -m "Update LLMWiki engine" && git push`.

An engine upgrade that isn't pushed hasn't happened for anyone else reading this wiki.
