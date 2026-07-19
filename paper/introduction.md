# 1. Introduction

<!-- Target: ~800 words. Status: OUTLINE STUB — @Vartan to draft. -->

## 1.1 Motivation: nutrition AI and the personalization gap

<!-- ~200 words.
- Diet-related disease burden in India (diabetes, obesity trends); cite ICMR / WHO data.
- Dietitian access is limited and expensive; AI assistants are increasingly consulted for diet advice.
- LLMs answer nutrition questions fluently but hallucinate and lack grounding — dangerous in a health domain. -->

## 1.2 The cultural grounding gap

<!-- ~200 words.
- Existing RAG nutrition systems anchor to USDA / Western databases [@khamesian2025nutrigen; @metaplate2025].
- Indian cuisine differs structurally: vegetarian-majority, regional diversity, distinct staples, Ayurvedic frameworks.
- Cultural-competence benchmarks show Western-default bias in health LLMs [@ccbench2026].
- Prior Indian food KBs exist (FKG.in [@fkgin2024]) but no end-to-end evaluated RAG system. -->

## 1.3 Research question and contributions

<!-- ~250 words. State RQ verbatim from the repo README:
"Can RAG-based systems provide culturally-appropriate and nutritionally-accurate
dietary guidance when trained on Indian-specific food databases and Ayurvedic principles?"

Contributions (bullet list):
1. CulRAG: first end-to-end, openly released RAG system for Indian dietary guidance
   (IFCT 2017 KB + regional/Ayurvedic attributes).
2. A transparent guardrail layer for constraint compliance and hallucination
   detection in food recommendation.
3. An evaluation framework + hand-labeled query set measuring retrieval quality
   and recommendation safety separately.
4. An interactive dashboard enabling user-feedback collection for future studies. -->

## 1.4 Paper structure

<!-- ~100 words. One sentence per section. -->
