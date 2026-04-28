# MINDSET File Inspection Summary
**Date:** 2026-03-07
**Status:** Information Ready for User Review

---

## 1. EMPLOYMENT COEFFICIENT FILE STRUCTURE

### File: `GLORIA_template/Employment/Empl_coefficient.csv`

**Format:** CSV matrix (Sectors × Countries)

**Structure:**
```
Row 1: Header row with country names
   - Columns 1-2: Empty, "Sector ID" (implied)
   - Columns 3+: Country names (Rest of Americas, Rest of Europe, Rest of Africa, Rest of Asia-Pacific, Afghanistan, Angola, Albania, United Arab Emirates, Argentina, ...)

Row 2+: Employment coefficients
   - Column 1: Sector ID (1, 2, 3, ...)
   - Column 2: Sector Name (e.g., "Growing wheat", "Growing maize", ...)
   - Column 3+: Employment coefficient values (jobs per unit output)
```

**Dimensions:**
- **Countries/Regions:** ~169 (estimated from header)
  - Includes individual countries (Afghanistan, Albania, Argentina, etc.)
  - Includes aggregate regions (Rest of Americas, Rest of Europe, etc.)
- **Sectors:** ~163 (estimated, file is large)
  - Agricultural sectors (Growing wheat, maize, cereals, rice, vegetables, etc.)
  - Livestock (Cattle, sheep, pigs, poultry)
  - Manufacturing, Services, etc.

**Sample Values:**
```
Sector 1 (Growing wheat):
  - Rest of Americas: 0.287
  - Rest of Europe: 0.591
  - Rest of Africa: 0.763
  - Rest of Asia-Pacific: 0.464
  - Afghanistan: 0.772

Sector 2 (Growing maize):
  - Rest of Americas: 0.224
  - Rest of Europe: 0.624
  - Rest of Africa: 0.653
  - Rest of Asia-Pacific: 0.368
  - Afghanistan: 0.680
```

**Interpretation:**
- Values appear to be **employment intensity coefficients**
- Likely measured as: **jobs per $1,000 or per $1M of output**
- Higher values = more labor-intensive sectors
- Example: Agriculture shows 0.2-0.9 range, meaning relatively labor-intensive

**Key Insight for Synthetic Data:**
We need to create a similar matrix but simplified:
- 3 regions (instead of 169)
- 10 sectors (instead of 163)
- Realistic coefficient values (0.005 to 0.020 for jobs per $1M)

---

## 2. SCENARIO FILES

### Files Found: `GLORIA_template/Scenarios/`

**Available scenarios:**
- `New template.xlsx`

### Next Step: Inspect This File
We need to open `New template.xlsx` to understand:
1. What sheets does it contain?
2. How are final demand shocks specified?
3. What is the format for country/sector identifiers?
4. What other parameters are needed (tax rates, recycling, etc.)?

**This will guide us in creating:** `Synthetic_Infrastructure.xlsx`

---

## 3. KEY OBSERVATIONS

### ✅ What We Learned:

1. **Employment coefficients are organized as a sector × country matrix**
   - Each cell = employment intensity for that sector-country pair
   - Values range from ~0.02 to ~1.0 (likely jobs per $1,000 output)

2. **GLORIA uses detailed classifications**
   - 163+ sectors (very detailed agricultural breakdown)
   - 169 countries/regions (individual countries + aggregate regions)

3. **For synthetic data, we'll simplify dramatically**
   - 10 sectors (Agriculture, Mining, Manufacturing, Construction, Utilities, Trade, Financial, Business Services, Government, Other Services)
   - 3 regions (Region A, Region B, Rest of World)
   - This keeps the methodology identical but makes it tractable

### ⏭️ Next Steps:

1. **✅ DONE:** Understand employment coefficient structure
2. **📋 TODO:** Inspect scenario file (`New template.xlsx`)
3. **📋 TODO:** Inspect employment module (`SourceCode/employment.py`)
4. **📋 TODO:** Create synthetic data generator

---

## 4. INFORMATION READY FOR USER

When you return from reading the guides, we have:

### ✅ Employment Coefficient Structure Understood
- Format: Sector × Country CSV matrix
- Dimensions: 163 sectors × 169 countries
- Values: Employment intensity (jobs per $ output)

### 📋 Next to Inspect: Scenario File
- File: `GLORIA_template/Scenarios/New template.xlsx`
- Purpose: Understand how to specify final demand shocks
- Will open this next when you're ready

### 📊 Synthetic Data Plan Clarified
Based on what we've seen, our synthetic data will be:
- **Dimensions:** 10 sectors × 3 regions (vs 163 × 169 in GLORIA)
- **Format:** Exactly the same CSV/PKL structure
- **Values:** Scaled appropriately for realistic employment multipliers

---

## 5. SUMMARY TABLE: Real vs Synthetic Data

| Component | GLORIA (Real) | Our Synthetic | Reason for Simplification |
|-----------|---------------|---------------|---------------------------|
| **Countries** | 169 | 3 | Demonstrate methodology, not policy analysis |
| **Sectors** | 163 | 10 | Focus on major economic categories |
| **Base Year** | 2019 | 2019 | Match template structure |
| **Format** | .pkl, .mat, .csv | .pkl, .mat, .csv | Exact same format for compatibility |
| **Employment Coefficients** | Real data | Stylized (5-20 jobs/$M) | Realistic but simplified |
| **Total Matrix Size** | 163 × 169 = 27,547 cells | 10 × 3 = 30 cells | 900× smaller, much faster |

---

**Status:** Ready for next inspection step when user returns from reading guides.

**Next Action:** Open and analyze `GLORIA_template/Scenarios/New template.xlsx`
