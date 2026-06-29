---
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
