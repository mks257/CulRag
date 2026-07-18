# Related Work

This file collects papers and resources relevant to CulRAG, organized by how they should be cited in the paper.

## Directly Indian — cite these in related work (most important)

1. FKG.in: A Knowledge Graph for Indian Food
   - arXiv: https://arxiv.org/pdf/2409.00830
   - Builds a knowledge graph covering Indian food using AI/LLM curation; documents the gap in Indian food knowledge bases.

2. Enhancing FKG.in: Automating Indian Food Composition Analysis
   - arXiv: https://arxiv.org/pdf/2412.05248
   - Follow-up comparing sources of Indian food composition data; tackles multilingualism and uncertainty; uses LLM agents for nutrition resolution.

3. Explainable Graph-RAG for Personalized Nutrition (Indian Thali)
   - Frontiers in AI (2026): https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1808444/full
   - Closest prior work; argues structured nutrition knowledge + cultural data are required for safe, consistent recommendations.

## LLM / RAG nutrition systems — baseline comparisons

4. NutriGen: Personalized Meal Plan Generator
   - arXiv: https://arxiv.org/abs/2502.20601
   - Code: https://github.com/SamanKhamesian/NutriGen
   - LLM framework anchored in USDA; useful for evaluation methodology and adapter code.

5. MetaPlate: Counterfactual-Guided RAG-LLM for Food Recommendation
   - arXiv: https://arxiv.org/pdf/2606.10120
   - RAG tool constraining meal generation to realistic USDA foods; useful prompt-engineering template.

6. HEI-Informed LLM-RAG Food Recommendations
   - arXiv: https://arxiv.org/abs/2605.15213

7. RAG-enhanced Llama 3 vs. off-the-shelf LLMs for dietary guidance
   - JMIR (2025): https://www.jmir.org/2025/1/e78625
   - Evaluation rubric template.

8. Evaluation of LLMs retrieving food/nutrition context for RAG
   - arXiv: https://arxiv.org/abs/2603.09704
   - Chroma-based retrieval study matching our stack.

## Benchmarks and evaluation methodology

9. FAM-Bench: Condition-Aware Food-as-Medicine Reasoning
   - arXiv: https://arxiv.org/pdf/2605.31410

10. CCBench-Health: Cultural Competence in Health Queries
    - arXiv: https://arxiv.org/html/2607.05405v1
    - Core motivation paper showing Western-default bias.

11. RAG Evaluation Survey
    - arXiv: https://arxiv.org/abs/2504.14891

12. RGB: Benchmarking LLMs in RAG
    - arXiv: https://arxiv.org/pdf/2309.01431

## Background / Foundational

13. RAG for LLMs: A Survey (Gao et al.)
    - arXiv: https://arxiv.org/abs/2312.10997

14. Nutrition-Related Knowledge Graph Neural Network (NRKG)
    - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC11241430/

---

Notes
-----
- The FKG.in pair (items 1–2) is especially relevant: cite as evidence of an active community and prior attempts at Indian KBs.
- Consider mining FAM-Bench and NutriGen code for evaluation and implementation ideas.

(Added to repository by project maintainers.)
