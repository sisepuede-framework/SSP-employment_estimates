# Fixing "Investment by" Approach - Investment Converter Sheet

## The Problem (Recap)
- Your Strategy files put PRODUCT codes in "Sector investing code*"
- Default INV_CONV has 0.19964 on diagonal (80% loss)
- This scales your $1M to ~$200K

## The Solution (Stay with Investment by)

Add an **"Investment converter"** sheet to each Strategy file that overrides the default INV_CONV with perfect 1:1 mapping.

## Investment Converter Sheet Structure

Based on scenario.py lines 444-446:

| Column Name | Description | Value |
|-------------|-------------|-------|
| **Country ISO*** | Country code | MEX, BGR, BLZ, etc. |
| **Investing sector code*** | Input (your products) | 1-120 |
| **Investment good sector code*** | Output (same products) | 1-120 |
| **Value*** | Conversion coefficient | 1.0 |
| **Type*** | Operation type | replace |

## What This Does

Tells MINDSET: "When sector N invests, convert 100% to product N"
- Sector 55 → 1.0 × Product 55 (not 0.19964 × Product 55)
- Sector 89 → 1.0 × Product 89 (not 0.19964 × Product 89)

## Full Specification

For 8 countries × 120 products = 960 rows:

```
Country ISO* | Investing sector code* | Investment good sector code* | Value* | Type*
ROW          | 1                      | 1                            | 1.0    | replace
ROW          | 2                      | 2                            | 1.0    | replace
...
ROW          | 120                    | 120                          | 1.0    | replace
BGR          | 1                      | 1                            | 1.0    | replace
BGR          | 2                      | 2                            | 1.0    | replace
...
MEX          | 1                      | 1                            | 1.0    | replace
MEX          | 2                      | 2                            | 1.0    | replace
...
```

## How to Implement

### Option A: Add Sheet to Each Strategy File
Create "Investment converter" sheet in each of your 469 Strategy files.

**Pros**: Self-contained
**Cons**: 469 files × 960 rows = lots of repetition

### Option B: Modify Default INV_CONV (RECOMMENDED)
Change the base INV_CONV file that MINDSET loads from 0.19964 to 1.0 on diagonal.

**Location**: Look for where INV_CONV is loaded in exog_vars_SSP.py
**Change**: Multiply diagonal by 5.009 (since 0.19964 × 5.009 ≈ 1.0)

### Option C: Create One Template Converter Sheet
Create a single template with 960 rows (8 countries × 120 sectors), then copy this sheet into each Strategy file.

## Remaining Issue: fcf_share Distribution

Even with INV_CONV fixed to 1.0:
- Investment starts in MEX for specific products
- fcf_share will distribute across producing countries
- This is CORRECT behavior - MEX invests $1M, but some products are imported

**Example**:
- MEX invests $10K in Product 55 (machinery)
- fcf_share says MEX imports 30% of machinery from USA
- Result: $7K demand for MEX machinery, $3K for USA machinery
- This is economically realistic!

## What Do You Prefer?

**Quick test option**: I can create a script that:
1. Modifies your INV_CONV data to have 1.0 on diagonal
2. Tests Strategy_1004_MEX
3. Shows if results are now reasonable

Then we decide whether to:
- Modify base INV_CONV permanently (Option B)
- Add converter sheets to all 469 files (Option C)
- Or something else

Should I create this test script?
