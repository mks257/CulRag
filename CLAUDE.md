# CulRAG

RAG system for culturally-grounded Indian dietary guidance (research paper project).

**Skills:** task-specific instructions live in [skills/README.md](skills/README.md).
Find the current task in its table and load that ONE skill file before working.

Quick facts: Python 3.13 venv at `.venv/`; run tests with
`.venv\Scripts\python.exe -m pytest tests/ -v`; installed libs are current-generation
(langchain 1.x, openai 2.x, `pinecone` not `pinecone-client`) — see
`skills/rag-pipeline/SKILL.md` before writing LLM/vector-DB code.
