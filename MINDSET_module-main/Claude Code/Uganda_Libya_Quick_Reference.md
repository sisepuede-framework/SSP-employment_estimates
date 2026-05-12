# Uganda & Libya Anomaly - Quick Reference

**Issue:** Employment estimates for Uganda and Libya are **20-100× higher** than normal

---

## The Problem (1 sentence)

Uganda and Libya show employment estimates of 272-2,051 jobs per $1M output, compared to the normal range of 10-50 jobs per $1M output for comparable countries.

---

## Root Cause (1 sentence)

The anomaly originates from abnormally small baseline output values (`q_base`) in GLORIA v57 data, which inflates employment multipliers through the formula: `empl_multiplier = EMPL_COEF × (empl_base / q_base)`.

---

## Where It Occurs (code location)

**File:** `SourceCode/employment.py`, **Lines:** 36-43

```python
self.empl_multiplier = empl_coef * (np.divide(empl_base, q_base, ...))
```

If `q_base` ≈ 0 → `empl_multiplier` → ∞

---

## What We Already Fixed

✓ **"Strategy as Purchases" logic** is correct (`RunMINDSET_EmploymentOnly_BATCH_FINAL.py`, lines 126-145)
- Investment correctly creates product demand
- Not the source of Uganda/Libya anomalies
- This confirms the issue is **base data quality**, not model logic

---

## Recommended Solution

**Use proxy country coefficients:**
- **Uganda** → Kenya or Tanzania (East African proxy)
- **Libya** → Tunisia or Egypt (North African proxy)

**Why:** Common practice in IO modeling when data quality is questionable

**Implementation:** ~1 hour of code modification + re-run 469 scenarios

---

## Documentation Completed

✓ **Workflow Guide** (`MINDSET_Workflow_Guide.md`) - detailed technical analysis
✓ **Presentation Slides** (`MINDSET_Employment_Presentation.tex`) - 3 new slides added
✓ **Summary Document** (`Uganda_Libya_Anomaly_Summary.md`) - full report
✓ **This Quick Reference** - for supervisor briefing

---

## Key Message

"The Uganda and Libya employment anomalies are caused by GLORIA v57 data quality issues, not by errors in our MINDSET implementation. Using proxy country coefficients (Kenya for Uganda, Tunisia for Libya) is a standard and defensible solution that will allow us to proceed with analysis while maintaining methodological rigor."

---

**Status:** Ready for supervisor discussion
**Next Step:** Get approval for proxy country approach
**Timeline:** Can implement solution this week once approved
