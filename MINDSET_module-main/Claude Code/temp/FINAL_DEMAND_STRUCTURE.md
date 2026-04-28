# Final Demand Sheet Structure for Strategy Files

## Column Structure

Based on MINDSET's scenario.py lines 214-217, the "Final demand" sheet expects:

| Excel Column Name | Internal Name | Description | Your Values |
|-------------------|---------------|-------------|-------------|
| **Producing country ISO*** | REG_exp | Where product is produced/sourced | See options below |
| **Consuming country ISO*** | REG_imp | Where product is consumed/invested | MEX (or BGR, BLZ, etc.) |
| **Product code*** | TRAD_COMM | Product being purchased (1-120) | Your 40 products |
| **FD code*** | PROD_COMM | Final demand category | **FD_4** (for investment) |
| **Value*** | Value | Investment amount | Your dk values |
| **Type*** | Type | How to apply the change | **abs-b** |

## FD Code Meanings

From scenario.py lines 254-256:
- **FD_1**: Household consumption (VIPA)
- **FD_3**: Government consumption (VIGA)
- **FD_4**: Gross fixed capital formation / Investment (VDFA) ← **USE THIS**
- FD_5, FD_6: Not implemented in current MINDSET version

## REG_exp (Producing Country): Three Options

### Option 1: All Domestic (Simplest)
Assume all products sourced domestically:
- REG_exp = MEX (same as REG_imp)
- **Pros**: Simple, matches your current assumption
- **Cons**: Unrealistic for products MEX doesn't produce

### Option 2: Use FCF_share (Most Realistic - RECOMMENDED)
Distribute based on baseline capital formation trade patterns:

For each product-country pair, split into multiple rows based on FCF_share:
```
Example for Product 55 in MEX with $10,000 investment:
If FCF_share shows MEX imports 30% from USA, 70% domestic:
  Row 1: REG_exp=MEX, REG_imp=MEX, TRAD_COMM=55, FD_4, Value=7000
  Row 2: REG_exp=USA, REG_imp=MEX, TRAD_COMM=55, FD_4, Value=3000
```

### Option 3: Manual Specification
If you know which products are imported, specify explicitly:
- Construction materials → domestic (REG_exp = MEX)
- Machinery → imports (REG_exp = USA, CHN, etc.)

## Type Values

From scenario.py lines 240-246:
- **abs-b**: Absolute value, spread proportionally to baseline ← **RECOMMENDED**
- abs: Absolute value, spread to current FD (for multi-year models)
- rel: Relative change (for multi-year models)
- rel-b: Relative to baseline (not implemented for investment)

Use **abs-b** for your case.

## Example Conversion

### Your Current Structure (Investment by sheet):
```
Country ISO* | Sector investing code* | Value*  | Type*
MEX          | 55                     | 10000   | abs-b
MEX          | 89                     | 42500   | abs-b
MEX          | 90                     | 42500   | abs-b
```

### Option 1: Simple Conversion (All Domestic)
```
Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type*
MEX                    | MEX                    | 55            | FD_4     | 10000  | abs-b
MEX                    | MEX                    | 89            | FD_4     | 42500  | abs-b
MEX                    | MEX                    | 90            | FD_4     | 42500  | abs-b
```

### Option 2: With FCF_share Distribution (Example)
```
Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value*  | Type*
MEX                    | MEX                    | 55            | FD_4     | 7000    | abs-b
USA                    | MEX                    | 55            | FD_4     | 2000    | abs-b
CHN                    | MEX                    | 55            | FD_4     | 1000    | abs-b
MEX                    | MEX                    | 89            | FD_4     | 38250   | abs-b
DEU                    | MEX                    | 89            | FD_4     | 4250    | abs-b
...
```

## Implementation Code

I can create a script to:
1. Read your current Strategy files (Investment by sheet)
2. Load FCF_share data from MRIO_BASE.FCF_BASE
3. Distribute each product across exporters based on FCF_share
4. Generate new Strategy files with "Final demand" sheet

## Advantages of Final Demand Approach

1. ✓ **No INV_CONV conversion** - products go directly to final demand
2. ✓ **No 80% scaling loss** - full $1M investment preserved
3. ✓ **Proper trade patterns** - uses FCF_share like investment module would
4. ✓ **Official MINDSET feature** - designed for this exact use case
5. ✓ **Clear semantics** - no confusion about "Sector investing code*" meaning

## Next Steps

Would you like me to:

**A)** Create a script that converts your existing Strategy files to use "Final demand" sheet with Option 1 (all domestic)?

**B)** Create a script that uses FCF_share to properly distribute across exporters (Option 2)?

**C)** First show you what FCF_share data looks like for MEX, so you can decide?

I recommend starting with **C** to see the trade patterns, then proceeding to **B** for realistic results.
