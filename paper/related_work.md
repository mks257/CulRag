# 2. Related Work

<!-- Target: ~1200 words. Status: OUTLINE STUB — @Vartan to draft.
Source material: RELATED_WORK.md in the repo root has links for every entry below. -->

## 2.1 Retrieval-augmented generation

<!-- ~200 words.
- RAG foundations [@lewis2020rag]; survey of RAG for LLMs [@gao2023ragsurvey].
- RAG benchmarking: RGB [@chen2023rgb], RAG evaluation survey [@rageval2025survey].
- Position: we apply RAG where grounding is a safety requirement, not just a quality boost. -->

## 2.2 LLMs and RAG for nutrition

<!-- ~350 words.
- NutriGen: LLM meal plans anchored in USDA [@khamesian2025nutrigen].
- MetaPlate: counterfactual-guided RAG constraining generation to real USDA foods [@metaplate2025].
- HEI-informed LLM-RAG recommendations [@heirag2026].
- RAG-enhanced Llama 3 vs. off-the-shelf LLMs for dietary guidance [@jmir2025rag] — evaluation rubric template.
- Retrieval evaluation for food/nutrition RAG on Chroma [@foodrageval2026] — closest to our retrieval stack.
- Gap: all anchor to Western databases; none model regional Indian cuisine or Ayurvedic attributes. -->

## 2.3 Indian food knowledge bases

<!-- ~300 words.
- FKG.in knowledge graph for Indian food [@fkgin2024] and its food-composition
  extension [@fkgin2024composition] — evidence of active community + documented KB gap.
- Explainable Graph-RAG for personalized nutrition (Indian Thali) [@thaligraphrag2026] —
  CLOSEST PRIOR WORK; compare directly: graph-based vs. our simpler vector RAG + guardrails;
  they argue structured cultural knowledge is required for safe recommendations, we test that claim end-to-end.
- IFCT 2017 as authoritative composition source [@longvah2017ifct]. -->

## 2.4 Safety, hallucination, and cultural competence

<!-- ~250 words.
- FAM-Bench: condition-aware food-as-medicine reasoning [@fambench2026].
- CCBench-Health: cultural competence in health queries [@ccbench2026] — core motivation.
- Nutrition knowledge-graph GNN approaches [@nrkg2024] as the structured alternative to RAG.
- Position our guardrails: rule-based, auditable hallucination detection vs. learned critics. -->

## 2.5 Summary of the gap

<!-- ~100 words. One paragraph: no prior system combines (i) an Indian-specific
composition KB, (ii) end-to-end RAG generation, (iii) transparent safety
guardrails, and (iv) a released evaluation framework. CulRAG fills this intersection. -->
