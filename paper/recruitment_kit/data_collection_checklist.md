# CulRAG Pilot Study — Data Collection Checklist

**STATUS: Draft for IRB Review**

⚠️ This document requires review and approval by [Your Institution] IRB/Ethics
Committee before use in any recruitment or data collection.

---

## Per-participant timeline

| Point | What | Instrument | Owner | Storage |
|-------|------|-----------|-------|---------|
| Pre-enrollment | Eligibility | screening_survey.md | Kavya | [SURVEY PLATFORM]; deleted if not enrolled |
| Enrollment | Consent record | consent_form.md | Kavya | [E-CONSENT SYSTEM / SIGNED PDF, restricted folder] |
| Enrollment | Assign pseudonymous ID (P01…) | ID key spreadsheet | Kavya | Separate restricted location; PI/Co-I access only |
| Week 0 | Baseline data | baseline_survey.md | Kavya | [SURVEY PLATFORM], keyed by P-ID |
| Weeks 1–4 | Usage + ratings + comments | Dashboard logs (automatic) | System | Study server, keyed by P-ID |
| Week 2 | Engagement + optional weight | weekly_checkin_template.md (Week 2) | Vartan | Email replies transcribed to P-ID sheet, originals deleted |
| Week 4 | SUS + satisfaction + feedback + optional weight | exit_survey.md | Vartan | [SURVEY PLATFORM], keyed by P-ID |
| Week 4 | Close access | Disable participant account/link | Kavya | — |

## Weekly operations checklist

- [ ] Monday: export dashboard feedback log; verify entries keyed by P-ID only
- [ ] Monday: check for zero-activity participants → friendly nudge (max 1/week)
- [ ] Any day: withdrawal email received → confirm, delete identifiable data on request, log withdrawal date
- [ ] Any day: distress or adverse report → pause participant, follow protocol §9, notify IRB if required

## Analysis handoff (Week 5)

- [ ] Merge baseline + usage + exit data on P-ID into one de-identified table
- [ ] Compute: completion rate, mean uses/week, % recommendations rated, mean rating, SUS scores
- [ ] Export open-text corpus for thematic coding (both coders)
- [ ] Verify no identifiers in the analysis dataset before it leaves restricted storage

## Data integrity rules

- Never join the ID key to analysis data except transiently for merges by PI.
- Optional fields (weight) stay optional — no follow-up pressure if blank.
- All storage locations, retention periods, and platforms must match what the
  IRB approved; if a tool changes, amend the protocol first.
