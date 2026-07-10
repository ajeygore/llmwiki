# LLMWiki Bootstrapping Instruction Manual for AI Agents

You are an AI coding assistant helping the user bootstrap a new personal knowledge base in this empty repository. Please follow these steps to initialize the LLMWiki:

## 1. Add the Engine
Place the engine repository (`https://github.com/ajeygore/llmwiki.git`) inside a folder named `llmwiki/` at the root of the user's workspace. There are two ways to do this — **default to Option A (vendoring)**, which works everywhere. Only use Option B if the workspace is already a Git repository and the user explicitly wants the engine kept as a linked submodule.

### Option A — Vendor the engine (recommended; works everywhere)
Clone the engine and remove its `.git` metadata so the files become a plain, committed part of the user's wiki repo:
```bash
git clone --depth 1 https://github.com/ajeygore/llmwiki.git llmwiki
rm -rf llmwiki/.git
```
This works whether or not the workspace is a Git repository, and teammates get the engine automatically on a normal `git clone` — no extra steps. To update the engine later, delete `llmwiki/` and re-run the two commands above.

### Option B — Git submodule (linked, for pulling upstream engine updates)
Only if the workspace is already a Git repository:
```bash
git submodule add https://github.com/ajeygore/llmwiki.git llmwiki
```
Warn the user that teammates must clone with `git clone --recursive` (or run `git submodule update --init` after cloning), and that engine updates are pulled later with `git submodule update --remote --merge`.

## 2. Run the Setup Script
Run the bootstrapping script to copy the entry template, agent manuals, and page skeletons from the engine to the workspace root:
- **On macOS/Linux:**
  ```bash
  ./llmwiki/setup.sh
  ```
- **On Windows:**
  ```cmd
  llmwiki\setup.bat
  ```

## 3. Verify Layout
Confirm that the root directory now contains:
- `index.html` (the viewer dashboard template)
- `agents.md` (the instruction manual for agents)
- `README.md` (the quickstart guide)
- `wiki/` (the folder containing `welcome.md`, `index.md`, etc.)
- `raw/` (the folder for raw source inputs)

## 4. Instruct the User (Important)
Once setup is complete, output a clear message containing:
1. **Commit Changes**: Warn the user that new files have been created in their workspace and they **MUST commit these changes** (`git add . && git commit -m "Initialize LLMWiki skeleton"`) to keep their git history clean.
2. **Start Server**: Instruct them to start the local viewer server:
   - On macOS/Linux: `./llmwiki/run`
   - On Windows: `llmwiki\run.bat`
3. **Agent Integration**: Tell them to open the wiki dashboard (typically on `http://localhost:8001`), locate the welcome page at `wiki/welcome.md`, copy the **AI Agent Setup Prompt**, and paste it into their coding agent chat to begin auto-populating the wiki!
