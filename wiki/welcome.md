---
title: Welcome
tags: [homepage, general]
summary: Welcome to your new LLMWiki workspace dashboard.
---

# Welcome to LLMWiki

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
