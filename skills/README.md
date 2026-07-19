# CulRAG Skills — the router

This folder is a library of **skills**: focused instruction files an AI assistant loads
one at a time. One skill per task keeps the assistant sharp — load ONLY the skill for the
task at hand, plus `culrag-context` if the assistant is new to the project.

**How to use (repo-reading agents — Claude Code, Cursor, Codex):** tell your assistant
which task you're doing; it loads the matching file below.

**Chat-only assistant (ChatGPT / Gemini in a browser)?** Open the skill file, copy its
whole content, paste it into the chat before asking for help.

## The table — find your task, load ONE skill

| Your task | Load this skill | Also load |
|---|---|---|
| Understand CulRAG: research question, architecture, team, phases | `culrag-context/SKILL.md` | — |
| Create or extend the food dataset (IFCT data, sample_foods.csv, data contract) | `building-food-data/SKILL.md` | `culrag-context/SKILL.md` |
| Work on the RAG pipeline (retriever, LLM chain, guardrails, vector DB) | `rag-pipeline/SKILL.md` | `culrag-context/SKILL.md` |
| Evaluate the system (precision@k, MRR, hallucination rate, eval queries) | `evaluating-rag/SKILL.md` | `culrag-context/SKILL.md` |
| Run baselines / ablations / comparison experiments for Results | `running-experiments/SKILL.md` | `evaluating-rag/SKILL.md` |
| Build or change the FastAPI server | `serving-api/SKILL.md` | `culrag-context/SKILL.md` |
| Literature review / deep research (find, read, log related work) | `deep-research/SKILL.md` | — |
| Write the paper with claims that hold (IEEE Access / Frontiers) | `writing-the-paper/SKILL.md` | `deep-research/SKILL.md` |
| Repo changed — sync the skills to match (end of session, upgrades, refactors) | `maintaining-skills/SKILL.md` | — |

## Rules for the assistant

1. Load the ONE skill matching the task. Don't load all of them.
2. Facts in skills (file paths, schemas, versions) reflect the repo at time of writing —
   verify against the repo if something looks stale, and update the skill file when it is.
3. Skills state *how this project does things*. Follow them over generic best practices.
