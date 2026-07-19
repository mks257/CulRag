# CulRAG Pilot Study Protocol: Feasibility and Usability of a Culturally Grounded AI Dietary-Guidance Dashboard

**STATUS: Draft for IRB Review**

⚠️ This document requires review and approval by [Your Institution] IRB/Ethics
Committee before use in any recruitment or data collection.

**Protocol version:** 0.1 (draft) · **Date:** 2026-07-18
**Principal Investigator:** Kavya Sri Meka · **Co-Investigator:** Vartan [LAST NAME]
**IRB protocol number:** [ASSIGNED BY IRB]

---

## 1. Summary

A 4-week, single-arm feasibility pilot (target N = 8–10) of CulRAG, a web
dashboard that provides culturally grounded Indian meal recommendations using
retrieval-augmented generation (RAG) over the Indian Food Composition Tables
(IFCT 2017) with automated safety guardrails. The pilot evaluates whether the
system is usable and engaging enough to justify a larger controlled study. It
is **not** designed to demonstrate clinical efficacy, and no efficacy claims
will be made from its results.

## 2. Objectives

**Primary (feasibility/usability):**
1. System usability: System Usability Scale (SUS) score at exit.
2. Adherence/engagement: frequency of dashboard use and of following
   recommendations, from usage logs and self-report.
3. Recommendation satisfaction: per-recommendation ratings (1–5) and exit
   satisfaction items.

**Secondary (qualitative):**
4. Perceived cultural appropriateness of recommendations (open-ended
   feedback, thematically coded).
5. Trust and comprehension of the guardrail/safety banners.

**Exploratory only:**
6. Self-reported weight change over 4 weeks. Reported descriptively as an
   exploratory observation; the design (no control group, small N, short
   duration, self-report) cannot support causal or efficacy conclusions.

## 3. Study Design

- Single-arm, open-label, 4-week pilot.
- Participants use the CulRAG dashboard at least 3 times per week to request
  meal recommendations, and rate recommendations they act on.
- Check-in emails at Week 2 and Week 4 (see `recruitment_kit/weekly_checkin_template.md`).
- All study activities are remote.

## 4. Participants

**Target:** N = 8–10 completers (recruit up to 14 to allow attrition).

**Inclusion criteria:**
- Adults 18–65 years old.
- Familiar with or interested in Indian cuisine; vegetarian or willing to
  receive vegetarian-leaning recommendations.
- Daily access to a smartphone or computer with internet.
- Able to read and respond in English.

**Exclusion criteria (safety):**
- Pregnant or breastfeeding.
- History of an eating disorder.
- Diagnosed condition requiring medically supervised diet (e.g., diabetes on
  insulin, chronic kidney disease, celiac disease under treatment).
- Currently under the care of a dietitian or physician for weight management.
- Food allergies so severe that accidental exposure is life-threatening
  (anaphylaxis), given the system's allergen screening is automated and not
  clinically validated.

Eligibility is assessed by the screening survey
(`recruitment_kit/screening_survey.md`).

## 5. Recruitment

- Channels: personal/professional networks, university mailing lists and
  flyers [CONFIRM CHANNELS WITH IRB].
- Interested individuals complete the screening survey; eligible respondents
  receive the consent form. No study activity occurs before documented
  consent.
- No compensation is offered in this pilot [OR SPECIFY — CONFIRM WITH IRB].

## 6. Intervention

The CulRAG dashboard (described in the companion system paper): participants
enter preferences (calorie target, vegetarian, regional preference, Ayurvedic
type, allergies, cooking time) and receive a single meal recommendation with
nutrition breakdown, cultural context, and a visible guardrail banner if any
automated safety check failed. Participants may follow or ignore any
recommendation.

**Important framing communicated to participants:** the system provides
informational suggestions, not medical or dietetic advice; it is displayed on
every dashboard page and in the consent form.

## 7. Data Collection

| Instrument | When | Mode | Data |
|---|---|---|---|
| Screening survey | Pre-enrollment | Form | Eligibility only |
| Consent form | Enrollment | Form/e-sign | Consent record |
| Baseline survey | Week 0 | Form | Demographics (minimal), diet preferences, self-reported weight (optional), tech comfort |
| Dashboard usage logs | Continuous | Automatic | Recommendation requests, ratings (1–5), comments (pseudonymous ID) |
| Week-2 check-in | Week 2 | Email + short form | Engagement, issues, optional weight |
| Exit survey | Week 4 | Form | SUS (10 items), satisfaction, optional weight, open feedback |

Details: `recruitment_kit/data_collection_checklist.md`.

## 8. Analysis Plan

- **Quantitative:** descriptive statistics only (means/medians, ranges,
  completion and adherence rates, SUS scoring per Brooke 1996). No
  inferential hypothesis tests are pre-specified; any p-values reported are
  exploratory.
- **Qualitative:** open-ended responses and dashboard comments thematically
  coded by two coders (PI + Co-I); disagreements resolved by discussion.
- **Attrition:** participants who withdraw are reported; their data are
  handled per Section 10.

## 9. Risks, Safety, and Ethics

- **Risk level:** minimal. The intervention suggests common foods; it does
  not restrict intake, prescribe supplements, or target clinical conditions.
- **Dietary-advice risk mitigation:** exclusion criteria remove participants
  who need supervised diets; every page carries the "informational, not
  medical advice" disclaimer; guardrail banners surface failed safety checks
  rather than hiding them; participants are told to consult a clinician for
  any medical concern and may stop at any time.
- **Allergen limitation disclosed:** automated allergen screening is
  keyword-based and NOT a safety guarantee; participants with severe
  allergies are excluded, and all participants are instructed to check
  ingredients themselves.
- **Distress/eating-behavior safeguard:** if a participant reports distress
  related to eating or body image, the team stops their participation and
  provides referral information [INSERT INSTITUTIONAL/NATIONAL RESOURCES].

## 10. Data Security and Privacy

- Participants are identified by a pseudonymous study ID; the key linking IDs
  to names/emails is stored separately, access-restricted to the PI/Co-I
  [SPECIFY STORAGE SYSTEM PER IRB REQUIREMENTS].
- Dashboard feedback is stored on the study server keyed by pseudonymous ID
  only; no names, emails, or precise locations are collected in-app.
- Survey data are stored in [SPECIFY: institution-approved survey platform].
- Self-reported weight is optional at every collection point.
- Retention: [X years per institutional policy]; on withdrawal, identifiable
  data are deleted on request (see consent form).
- Any publication reports aggregate or de-identified data only; quotes are
  used only with the consent-form permission and stripped of identifiers.

## 11. Consent and Withdrawal

Documented informed consent (`recruitment_kit/consent_form.md`) before any
data collection. Participation is voluntary; withdrawal at any time, without
reason, with no consequence; on withdrawal, collected identifiable data are
deleted on request.

## 12. Timeline (relative to IRB approval)

| Week | Activity |
|---|---|
| −4 to −1 | IRB review [expedited requested; standard review may add 2–4 weeks] |
| 0 | Recruitment + screening + consent |
| 1 | Baseline survey; dashboard access opens |
| 2 | Check-in #1 |
| 4 | Check-in #2 + exit survey; access closes |
| 5–6 | Analysis; results feed Paper 2 |

## 13. IRB Submission Checklist

- [ ] This protocol
- [ ] Consent form (`recruitment_kit/consent_form.md`)
- [ ] All surveys and email templates (`recruitment_kit/`)
- [ ] Recruitment materials/flyer text [TO DRAFT if flyers used]
- [ ] Data-management plan details (storage systems, retention period)
- [ ] PI/Co-I human-subjects training certificates (e.g., CITI) [CONFIRM]
- [ ] IRB application form [INSTITUTION-SPECIFIC]
