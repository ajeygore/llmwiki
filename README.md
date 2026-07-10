# LLMWiki — LLMWiki

LLMWiki is a lightweight, zero-build personal knowledge base engine that bridges the gap between human readers and AI agents. It enables humans to read wiki pages as beautiful, rich, responsive HTML in their browser, while allowing AI agents to read and modify raw Markdown files directly in the codebase.

This project is a complete implementation of Andrej Karpathy's [LLM Wiki architecture design pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### 🛠️ About Setup
Setting up a new wiki workspace is straightforward. Because the LLMWiki engine is designed to live inside target workspaces as a self-contained `/llmwiki/` folder, you simply add the engine inside any empty directory — by **vendoring** it (a shallow clone with its `.git` removed) or as a **git submodule** — and then run the bootstrapping script (or delegate it to an AI assistant). The script populates the workspace root with standard agent manuals (`agents.md`), the index template (`index.html`), and initial markdown directory schemas (`/wiki/`) ready for content population.

---

## 🔄 How It Works & Migration Flow

LLMWiki separates your **agent workspace configs** (memories, rules, custom skills) from your **active project source code**. This ensures a clean project repo while keeping all agent collective knowledge shareable in a separate wiki repository.

### The Lifecycle:
1. **Set the Engine**: Add the `llmwiki` engine into an empty wiki repository — either **vendor** it (clone + drop `.git`) or add it as a **git submodule**.
2. **Launch & Browse**: Run the local server (`./llmwiki/run`) to start the browser dashboard.
3. **Connect Your Coding Agent**: Open your main project work directory in your AI coding workspace, and paste the bootstrap welcome prompt.
4. **Link Workspace Rules**: Tell your coding agent in the project workspace configuration (`AGENTS.md` or `.agents/AGENTS.md`) that instead of local project-specific instruction folders and ad-hoc files, **all rules, context, and skills are maintained centrally in your wiki repository**.
5. **Share with the Team**: Commit and push the wiki repository. Now, the entire team shares the same collective agent context, and agents can read/update it collaboratively without contaminating the project code.

### 🚚 Migrating Existing Agent Workspaces:
If you already have a set of project instructions, active context states, or custom skills, simply ask your coding agent to migrate them:
> *"Migrate all my current project context, custom skills, and AGENTS.md rules over to my LLMWiki directory located at <local_path_to_wiki_root>."*
The agent will organize them into `wiki/context.md`, `agents.md`, and the `wiki/skills/` directory.

---

## 📁 Repository Layout

> **Note:** This repository *is* the engine — its root contains the scripts (`setup.py`/`setup.sh`/`setup.bat`, `run`, `search`, `llmwiki.js`, `style.css`) that get cloned into your workspace's `/llmwiki/` folder. The layout below describes the **wiki workspace** that `setup.py` generates around the engine, not this repo.

- `/raw/` — Immutable source documents (articles, PDFs, transcriptions) to be processed.
- `/wiki/` — Structured, LLM-maintained Markdown pages.
- `/wiki/index.md` — The dynamic index catalog parsing sidebar links and groups.
- `/wiki/log.md` — Chronological action log.
- `/wiki/overview.md`, `memory.md`, `context.md` — Workspace and session meta-context.
- `/llmwiki/` — The rendering engine core.
- `/index.html` — The customizable entry point layout.
- `/agents.md` — Instruction manual for AI agents.

---

## 🛠️ Installation & Setup

You can bootstrap a brand new wiki repository automatically using an AI coding assistant (like Claude Code, Cursor, Gemini, or Antigravity), or perform the steps manually.

### Option A: Automate with an AI Coding Assistant (Recommended)

1. Create a new empty folder on your computer and open it in your AI coding assistant workspace.
2. Copy and paste the following prompt into the agent's chat:
   ```markdown
   Please read the LLMWiki bootstrapping instruction manual from this URL:
   https://raw.githubusercontent.com/ajeygore/llmwiki/main/setup.md
   Follow its instructions to initialize the LLMWiki repository inside this empty directory.
   ```
3. The assistant will read the manual, add the engine (vendored or as a submodule), run the setup script, and guide you to commit the files.

### Option B: Manual Setup

#### Step 1: Add the Engine
Place the engine inside a `llmwiki/` folder at the root of your wiki workspace. Pick **one** of the two methods below.

**Option A — Vendor the engine (recommended; works everywhere, even if your workspace isn't a git repo):**
```bash
git clone --depth 1 https://github.com/ajeygore/llmwiki.git llmwiki
rm -rf llmwiki/.git
```
The engine becomes plain files committed into your own repo, so teammates get it on a normal `git clone`. Update later by deleting `llmwiki/` and re-running the two commands.

**Option B — Git submodule (keeps the engine linked for easy upstream updates; requires your workspace to already be a git repo):**
```bash
git submodule add https://github.com/ajeygore/llmwiki.git llmwiki
```
Note: teammates must clone with `git clone --recursive` (or run `git submodule update --init` afterward).

#### Step 2: Bootstrap the Directory Structure
Run the bootstrapping script to copy the core HTML viewer, agent schemas, and markdown page skeletons to the parent repository root.

- **On macOS/Linux:**
  ```bash
  ./llmwiki/setup.sh --name "LLMWiki"
  ```
- **On Windows (CMD/PowerShell):**
  ```cmd
  llmwiki\setup.bat --name "LLMWiki"
  ```
*(The `--name` parameter is optional and defaults to "LLMWiki")*

---

## ⚡ Starting the Server

To launch the local web server and automatically open the wiki viewer dashboard in your default browser:

- **On macOS/Linux:**
  ```bash
  ./llmwiki/run
  ```
- **On Windows:**
  Double-click `llmwiki\run.bat` or run:
  ```cmd
  llmwiki\run.bat
  ```

---

## 🤖 Integrating AI Agents

To start collaborating with an AI coding assistant, copy the prompt instruction block displayed on your dashboard's welcome page (`#/wiki/welcome.md`) and paste it to prime your assistant. It will read `agents.md` and use Ingest, Query, and Lint workflows to maintain your knowledge vault.

### Command Line Search CLI
AI agents (and humans) can quickly query the local knowledge database directly from the command line:

- **On macOS/Linux:**
  ```bash
  ./llmwiki/search "<query_term>"
  ```
- **On Windows:**
  ```cmd
  llmwiki\search.bat "<query_term>"
  ```

---

## 🔄 Fetching Engine Updates

Pull down new features, UI layouts, or search fixes without touching your wiki pages. How you update depends on how you added the engine:

**If you vendored it (Option A):** replace the folder with a fresh copy —
```bash
rm -rf llmwiki && git clone --depth 1 https://github.com/ajeygore/llmwiki.git llmwiki && rm -rf llmwiki/.git
```

**If you added it as a submodule (Option B):** fetch and merge from the remote engine repo —
```bash
git submodule update --remote --merge
```
