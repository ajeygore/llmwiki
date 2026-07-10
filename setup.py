#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime

def create_file_if_missing(filepath, content, description):
    if os.path.exists(filepath):
        print(f"ℹ️  File already exists, skipping: {os.path.basename(filepath)}")
    else:
        print(f"📝 Creating {description}: {os.path.basename(filepath)}...")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser(description="LLMWiki Bootstrapping Engine")
    parser.add_argument('--name', default="LLMWiki", help="The name of your Wiki knowledge base")
    args = parser.parse_args()
    
    wiki_name = args.name
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    wiki_root = os.path.abspath(os.path.join(engine_dir, '..'))
    
    print("-" * 50)
    print("🚀 Initialising LLMWiki Repository Skeleton...")
    print(f"📂 Engine Location: {engine_dir}")
    print(f"📂 Wiki Root:       {wiki_root}")
    print(f"📛 Wiki Name:       {wiki_name}")
    print("-" * 50)
    
    # 1. Create Raw Folder README
    raw_readme_path = os.path.join(wiki_root, 'raw', 'README.md')
    raw_readme_content = """# Raw Sources Folder

Drop your immutable raw source documents here (articles, papers, PDF extracts, journal entries).
AI Agents should read these files to ingest new knowledge into the `/wiki/` folder, but MUST NEVER modify them.
"""
    create_file_if_missing(raw_readme_path, raw_readme_content, "raw folder readme")
    
    # 2. Create index.html template
    index_html_path = os.path.join(wiki_root, 'index.html')
    index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{wiki_name}</title>
  
  <!-- Google Font: Roboto -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  
  <!-- Markdown Parser (Marked) -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  
  <!-- Syntax Highlighting (Prism) -->
  <link id="prismThemeLink" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
  
  <!-- Engine Styling -->
  <link rel="stylesheet" href="llmwiki/style.css">
</head>
<body class="dark-mode">
  <div class="app-container">
    
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="wiki-title">{wiki_name}</div>
        <button class="mobile-close" id="mobileCloseBtn" aria-label="Close navigation">✕</button>
      </div>
      
      <div class="sidebar-filter-wrapper">
        <div class="search-input-wrapper" style="border-radius: 6px; padding: 4px 8px;">
          <input type="text" id="searchInput" placeholder="Filter sidebar..." autocomplete="off">
        </div>
      </div>
      
      <nav class="sidebar-nav" id="sidebarNav">
        <!-- Rendered dynamically by loadSidebar() -->
      </nav>
      
      <div class="sidebar-footer">
        <button id="themeToggle" class="mode-toggle">
          <span class="mode-icon">🌙</span>
          <span class="mode-text">Dark Mode</span>
        </button>
      </div>
    </aside>
    
    <!-- Sidebar overlay for mobile devices -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    
    <!-- Main Content Area -->
    <main class="main-content">
      <header class="content-header">
        <button class="mobile-toggle" id="mobileToggleBtn" aria-label="Open navigation">
          <span></span>
          <span></span>
          <span></span>
        </button>
        
        <div class="breadcrumb" id="breadcrumb">
          <span class="crumb">wiki</span>
          <span class="crumb-separator">/</span>
          <span class="crumb active" id="currentCrumb">index.md</span>
        </div>

        <!-- Material Search Bar with Floating Dropdown -->
        <div class="header-search-container">
          <div class="search-input-wrapper">
            <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input type="text" id="globalSearchInput" placeholder="Search pages, tags, content..." autocomplete="off">
            <button id="clearSearchBtn" class="clear-search-btn" aria-label="Clear search" style="display: none;">✕</button>
          </div>
          <div id="searchDropdown" class="search-dropdown" style="display: none;"></div>
        </div>
        
        <div class="meta-info">
          <a href="#" id="rawLink" target="_blank" class="raw-btn">
            <svg class="raw-icon" viewBox="0 0 24 24" width="14" height="14">
              <path fill="currentColor" d="M12.89 3L14.85 3.4L11.11 21L9.15 20.6L12.89 3M19.59 12L16 8.41V5.58L22.42 12L16 18.41V15.58L19.59 12M1.58 12L8 5.58V8.41L4.41 12L8 15.58V18.41L1.58 12Z"/>
            </svg>
            Raw MD
          </a>
        </div>
      </header>
      
      <div class="content-wrapper">
        <article class="markdown-body" id="content">
          <div class="loading-placeholder">Loading wiki content...</div>
        </article>
      </div>
    </main>
    
  </div>

  <!-- Engine Scripts -->
  <script src="llmwiki/llmwiki.js"></script>
</body>
</html>
"""
    create_file_if_missing(index_html_path, index_html_content, "root human HTML viewer template")
    
    # 3. Create agents.md instruction manual
    agents_md_path = os.path.join(wiki_root, 'agents.md')
    agents_md_content = """# LLMWiki Agent Instructions

This repository is an **LLMWiki** knowledge base. It is designed to be maintained entirely by LLM agents in collaboration with the user, following the architecture outlined in [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

---

## Directory Layout

- `/raw/` — Immutable raw source documents (articles, PDFs, logs) that the agent reads but never modifies.
- `/wiki/` — The directory containing all wiki markdown files (concepts, summaries, logs, etc.).
- `/wiki/index.md` — The content catalog containing links and summaries of all pages. Used by the browser engine to construct the navigation sidebar.
- `/wiki/log.md` — The chronological action log.
- `/wiki/skills/` — Custom workspaces-specific skills directory. Each subfolder contains a specialized agent skill.
- `/llmwiki/` — The LLMWiki rendering engine (JS and CSS assets).
- `/index.html` — The customizable HTML template for human browsing.
- `/agents.md` — This instruction manual.

---

## Operating Guidelines for Agents

When the user asks you to interact with this wiki, you must follow the guidelines for the respective operational flow:

### 1. Ingestion Flow (Adding a Source)
1. **Read and Extract**: Read the raw source provided by the user (usually located under a `/raw/` folder, or provided directly in the prompt). Summarize the key claims and information.
2. **Draft the Summary**: Write a new markdown file in `/wiki/` summarizing the source. Use clear headings, YAML frontmatter tags, and proper citations.
3. **Cross-Reference**:
   - Update existing concept or topic files in `/wiki/` to integrate the new knowledge.
   - Link between files using relative markdown links (e.g., `[Welcome](welcome.md)` or `[Getting Started](getting-started.md)`).
4. **Update Catalog**: Add the new file link and a brief one-line description to `/wiki/index.md`.
5. **Log the Action**: Append an entry to `/wiki/log.md` with the timestamp and action name.

### 2. Query Flow (Answering Questions)
1. **Discover & Search**: Search for relevant terms using the CLI tool `./llmwiki/search "<query>"` or read `/wiki/index.md` to find relevant files.
2. **Synthesize**: Read the matching files and generate an answer citing the relevant pages.
3. **File Back (Compounding)**: If the answer is complex, involves synthesis across multiple files, or presents a useful comparison table, **file it back into the wiki** as a new markdown page (e.g. under a `/wiki/comparisons/` or `/wiki/synthesis/` subdirectory). Link it to `/wiki/index.md` and log the creation.

### 3. Lint Flow (Consistency & Health Check)
Periodically (or when asked), run a lint pass to keep the wiki healthy. Identify and address:
1. **Contradictions**: Discrepancies between older summaries and newer claims. Flag these to the user or reconcile them.
2. **Stale Claims**: Superseded facts that are no longer accurate based on newer documents.
3. **Orphan Pages**: Pages in `/wiki/` that have no inbound links from the rest of the wiki (or are missing from `wiki/index.md`).
4. **Data Gaps & Missing Links**: Concepts mentioned on pages that would benefit from having their own page or linking to an existing page.

---

## 🛠️ Workspace Custom Skills (`/wiki/skills/`)

Custom coding agent capabilities can be packaged as skills inside `/wiki/skills/<skill_name>/`. Visiting agents must load and follow these skills:
- **`SKILL.md`**: Main manifest defining frontmatter `name` and `description` + instruction rules.
- **`references/`**: Place API manuals, library specs, or database schemas in this folder. Keep files short and split to remain token-efficient.
- **`scripts/`**: Helper scripts the agent can run.

### 🔄 Loops & Scheduling Policies
If executing automated loops or scheduled agent flows (cron triggers, cron iteration timer schedules):
- **Safety Terminations**: All agent execution loops MUST declare a clean early-termination condition (e.g., "stop when `/raw/` is empty" or a maximum limit of 5 consecutive iterations).
- **Scheduled Runs**: Automations running on system schedules (like hourly indexing or daily lint runs) must document their cron schedules in `wiki/skills/` and log execution metrics to `/wiki/log.md`.

---

## File and Link Conventions
- Maintain a clean hierarchy.
- Use relative links without folders if the file is in the same directory (e.g., `[Welcome](welcome.md)`).
- Prefix pages with YAML frontmatter containing `title`, `tags`, and `summary` tags:
  ```yaml
  ---
  title: Page Title
  tags: [tag1, tag2]
  summary: Brief one-sentence summary.
  ---
  ```
- **Never** break the structure of `/wiki/index.md` as it is parsed by the client-side viewer.

---

## Log Formatting
All logs in `/wiki/log.md` must use the parseable prefix format:
`## [YYYY-MM-DD] action | Description`
This makes the logs parseable via unix command-line tools.
"""
    create_file_if_missing(agents_md_path, agents_md_content, "Agent manual instructions")
    
    # 4. Create README.md
    readme_path = os.path.join(wiki_root, 'README.md')
    readme_content = f"""# {wiki_name} — LLMWiki

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
  ./llmwiki/setup.sh --name "{wiki_name}"
  ```
- **On Windows (CMD/PowerShell):**
  ```cmd
  llmwiki\\setup.bat --name "{wiki_name}"
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
  Double-click `llmwiki\\run.bat` or run:
  ```cmd
  llmwiki\\run.bat
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
  llmwiki\\search.bat "<query_term>"
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
"""
    create_file_if_missing(readme_path, readme_content, "Quickstart README")
    
    # 5. Create wiki/index.md catalog
    catalog_path = os.path.join(wiki_root, 'wiki', 'index.md')
    catalog_content = f"""# Wiki Directory

Welcome to the {wiki_name} catalog. This catalog is parsed by the LLMWiki engine to generate the navigation sidebar.

## Navigation
- [Welcome](welcome.md) — Welcome to {wiki_name}
- [Getting Started](getting-started.md) — Quick start guide

## Meta Context
- [Overview](overview.md) — Directory overview and structure
- [Memory](memory.md) — Long-term compiled agent memories
- [Context](context.md) — Operational context and session state

## Operations
- [Activity Log](log.md) — Chronological history of modifications

## Custom Skills
- [Example Skill](skills/example-skill/SKILL.md) — Demonstration of agent capabilities and loop policies
"""
    create_file_if_missing(catalog_path, catalog_content, "wiki directory index")
    
    # 6. Create wiki/welcome.md page
    welcome_path = os.path.join(wiki_root, 'wiki', 'welcome.md')
    welcome_content = f"""---
title: Welcome
tags: [homepage, general]
summary: Welcome to your new {wiki_name} workspace dashboard.
---

# Welcome to {wiki_name}

> [!IMPORTANT]
> Updates to this page are done through LLMs or code assist agents themselves. If you are using this wiki, please make sure that you have commit writes or PR writes to this wiki. **DO NOT WORK** with this if you do not have these rights.

This is the homepage of your newly initialized wiki knowledge base. It is designed to compile, organize, and persistently store your notes, concepts, and project details in cooperation with AI agents.

---

## 📖 What is LLMWiki?

LLMWiki is a zero-compilation, static markdown knowledge base. While **AI Agents** interact directly with the raw markdown files inside this directory, **Humans** view these files through a beautiful, dynamic browser dashboard. 

The wiki serves as a **compounding, persistent memory bank** that gets richer with every source you ingest.

---

## 🤖 AI Agent Setup Prompt

Copy and paste this prompt into your AI coding assistant (e.g. Claude Code, Gemini CLI, Cursor, or Antigravity) to bootstrap its interaction with this wiki:

```markdown
You are an AI assistant helping me maintain my personal knowledge base in this repository.
The wiki content root is at `/wiki/`. The `/llmwiki/` folder contains only the HTML rendering engine. We NEVER modify any files inside the `/llmwiki/` engine folder, as the engine lives in a separate repository at https://github.com/ajeygore/llmwiki.
We have initialized an LLMWiki structure.

Please read the schema instructions in `agents.md` at the root of the repository.
When working in this directory:
1. Read the instructions in `agents.md` to follow Ingestion, Query, and Lint flows.
2. Ensure that you write all long-term memories and persistent takeaways in `wiki/memory.md`.
3. Update the directory overview in `wiki/overview.md` when files/folders change.
4. Update `wiki/context.md` to persist session progress.
5. Always catalog new pages in `wiki/index.md` and log updates in `wiki/log.md`.
```

---

## 🚀 Quick Actions

- **Review Setup**: Read the [Getting Started](getting-started.md) page to learn how to operate this wiki.
- **Track Updates**: Check the [Activity Log](log.md) to inspect the history of modifications.
- **Instruct Your Agent**: Refer to the [agents.md](../agents.md) file at the root to check agent instructions.

---

## 📁 Catalog Directory

The main catalog is populated dynamically. You can click on the **Explore Catalog** option in the sidebar navigation or click [here](index.md) to search tags, browse directories, and review page grids.
"""
    create_file_if_missing(welcome_path, welcome_content, "welcome page")
    
    # 7. Create wiki/getting-started.md guide
    guide_path = os.path.join(wiki_root, 'wiki', 'getting-started.md')
    guide_content = """---
title: Getting Started
tags: [guide, help, setup]
summary: A guide outlining how humans and agents operate this knowledge base.
---

# Getting Started

This guide explains how to use and operate your LLMWiki.

## For Humans
- Serve this wiki locally using `llmwiki/run` from the root directory.
- Browse the formatted HTML page in your web browser.
- Search or filter topics using the sidebar search box.
- Customize the styles in `llmwiki/style.css` if desired.

## For AI Agents
- Treat the `/wiki/` folder as the permanent knowledge source.
- Add summaries and index them in `wiki/index.md` when ingesting new materials.
- Log modifications in `wiki/log.md`.
- Follow the guidelines in `agents.md` at the root of the repository.
"""
    create_file_if_missing(guide_path, guide_content, "getting started guide")
    
    # 8. Create wiki/log.md chronological log
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(wiki_root, 'wiki', 'log.md')
    log_content = f"""---
title: Activity Log
tags: [operations, log]
summary: A chronological log tracking all wiki updates and modifications.
---

# Activity Log

This is an append-only log of modifications, updates, and indexing runs performed on the wiki. All logs use the parseable prefix format: `## [YYYY-MM-DD] action | description`.

## [{date_str}] init | Initialize {wiki_name} repository.
- Created `agents.md`, `index.html`, `README.md`.
- Created skeleton documents: `welcome.md`, `getting-started.md`, `index.md`, `log.md`, `overview.md`, `memory.md`, `context.md`.
"""
    create_file_if_missing(log_path, log_content, "wiki activity log")
    
    # 9. Create wiki/overview.md structural overview
    overview_path = os.path.join(wiki_root, 'wiki', 'overview.md')
    overview_content = """---
title: Overview
tags: [meta, structure]
summary: Repository overview and active directories layout description.
---

# Workspace Overview

This document provides an overview of the working directory structure and high-level files in this repository.

## Project Structure
- `agents.md` — The global instruction manual governing AI agent processes.
- `index.html` — The client-side dashboard viewer template.
- `llmwiki/` — The rendering engine core.
- `raw/` — Immutable source documents to be processed.
- `wiki/` — The structured, LLM-maintained knowledge vault.
"""
    create_file_if_missing(overview_path, overview_content, "wiki overview page")
    
    # 10. Create wiki/memory.md long term memory
    memory_path = os.path.join(wiki_root, 'wiki', 'memory.md')
    memory_content = """---
title: Memory
tags: [meta, memory, learnings]
summary: A compiled record of long-term agent memories and persistent takeaways.
---

# Agent Memory

This file acts as a persistent memory bank where visiting AI agents document long-term learnings, persistent takeaways, and critical knowledge compiled across sessions.

## Long-term Learnings
- Initial setup completed.
"""
    create_file_if_missing(memory_path, memory_content, "wiki memory page")
    
    # 11. Create wiki/context.md session progress log
    context_path = os.path.join(wiki_root, 'wiki', 'context.md')
    context_content = """---
title: Context
tags: [meta, context, state]
summary: Active session meta-context, handoffs, and current operational states.
---

# Meta Context

This file tracks active session state, progress, and agent handoffs between task iterations.
"""
    create_file_if_missing(context_path, context_content, "wiki context page")
    
    # 12. Create wiki/skills/example-skill/SKILL.md
    skill_md_path = os.path.join(wiki_root, 'wiki', 'skills', 'example-skill', 'SKILL.md')
    skill_md_content = """---
name: example-skill
description: An example custom agent skill template showing how to layout rules, references, loops, and scheduled tasks.
---

# Example Agent Skill Template

This directory showcases the structure for declaring custom agent skills, references, and automation procedures.

## 📁 Skill Structure Layout
- `SKILL.md` — The main instruction manifest (this file) containing metadata tags in frontmatter.
- `references/` — Subdirectory containing long-form reference documentation, API specs, or coding guidelines.
- `scripts/` — Subdirectory for helper utilities or diagnostic scripts the agent can execute.

---

## 🔄 Loops, Recursion, and Scheduled Workflows

To execute periodic or repetitive actions (such as indexing, health sweeps, or cron-like runs), agents should configure:

### 1. Scheduled Cron Tasks
Use scheduling mechanisms (like cron or system timers) to trigger periodic agent invocations. For example:
- **Index Refresher**: Run an indexing agent every 6 hours to scan for new raw files.
- **Lint Sweep**: Run a consistency lint agent every 24 hours to find orphans or stale facts.

### 2. Early-Terminating Loops
When working on multi-step workflows (e.g. batch-processing multiple raw PDFs), configure explicit timer conditions or sender-specific triggers to avoid runaway execution loops.
Always establish:
- A clear termination condition (e.g., "stop when `raw/` is empty").
- A maximum iteration count (e.g. limit execution to 5 consecutive runs).
"""
    create_file_if_missing(skill_md_path, skill_md_content, "example skill manifest")

    # 13. Create wiki/skills/example-skill/references/README.md
    skill_ref_path = os.path.join(wiki_root, 'wiki', 'skills', 'example-skill', 'references', 'README.md')
    skill_ref_content = """# Skill References

Place long-form API specifications, database schemas, library guides, or coding style documents here.
This keeps the main `SKILL.md` instruction file short and token-efficient, while allowing agents to load references on-demand when performing skill tasks.
"""
    create_file_if_missing(skill_ref_path, skill_ref_content, "example skill references readme")
    
    print("-" * 50)
    print(f"✅ {wiki_name} Repository Skeleton Ready!")
    print("💡 Start your server by running: ./llmwiki/run")
    print("-" * 50)

if __name__ == '__main__':
    main()
