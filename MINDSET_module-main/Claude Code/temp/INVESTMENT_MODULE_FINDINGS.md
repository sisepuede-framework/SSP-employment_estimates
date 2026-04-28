# INVESTMENT MODULE ANALYSIS: Key Findings

## Summary

The "incredibly off" employment results are caused by MINDSET's investment module applying transformations that don't match your data structure.

## How MINDSET Investment Module Works

### Design Intent
- **"Sector investing code*"** = WHO invests (the SECTOR that is investing)
- **INV_CONV matrix** = Converts from investing sector → products purchased
- **fcf_share** = Distributes product purchases across exporting countries

### Example
If "Construction sector invests $1M":
1. INV_CONV converts: Construction → (cement, steel, machinery, etc.)
2. fcf_share distributes: Where to buy each product (domestic vs imports)

## Your Data Structure

According to your Strategy files and template:
- **"Sector investing code*"** = WHAT to purchase (product codes 1-120)
- **Values** = Investment amount per product
- **Total** = $1,000,000 across 40 products

This is ALREADY a final demand vector - no conversion needed.

## What Happens When You Use INV_model

### The Default INV_CONV Matrix
- 120×120 diagonal matrix
- Diagonal values = 0.19964 (≈20%)
- Off-diagonal = 0.0

This means: Sector N → 0.19964 × Product N

### Problem 1: Scaling
Your $1M investment gets scaled by 0.19964:
- Input: $1,000,000
- After INV_CONV: $199,640
- **Loss: 80% of investment value**

### Problem 2: fcf_share Redistribution
The remaining 20% gets redistributed across countries using fcf_share (capital formation patterns), which further distorts your intended allocation.

### Result from compare_direct_vs_converted.py
- **Correlation: -0.0127** (essentially no relationship)
- MEX Sector 89: $42,500 → $0 (disappeared)
- ROW Sector 86: $0 → $303,223 (appeared from nowhere)

## Why Direct Approach Also Failed

The RUN_ONE_SCENARIO_DIRECT.py approach:
```python
inv_demand['TRAD_COMM'] = inv_demand['PROD_COMM']  # Rename: product codes
inv_demand['REG_exp'] = inv_demand['REG_imp']      # Domestic purchases
```

Problems:
1. **REG_exp = REG_imp assumes ALL purchases are domestic**
   - Reality: Some products must be imported
   - Should use fcf_share to determine import sources

2. **Missing trade patterns**
   - When MEX invests in Product 55, where does that product come from?
   - fcf_share contains this information from baseline data

## The Correct Solution

### Option 1: Use "Final demand" Sheet (RECOMMENDED)

MINDSET has a dedicated "Final demand" sheet for direct product specifications:

**Structure:**
- Producing country ISO*
- Consuming country ISO*
- Product code*
- FD code*
- Value*
- Type*

This is EXACTLY what your data represents - direct specification of products and trade flows.

**Workflow:**
1. Convert your Strategy files to use "Final demand" sheet instead of "Investment by"
2. Specify:
   - Producing country: Where product comes from (use fcf_share to determine)
   - Consuming country: MEX (your focal country)
   - Product code: Your 40 products
   - Value: Your investment amounts

3. Use scenario.set_fd_exog() instead of set_exog_inv()
4. Skip investment module entirely

### Option 2: Use fcf_share in Direct Approach

If you want to keep "Investment by" sheet:

```python
# 1. Load investment data (products and amounts)
inv_exog = Scenario.inv_exog  # REG_imp, PROD_COMM, dk

# 2. Distribute across exporters using fcf_share
fcf_share = MRIO_BASE.FCF_BASE  # Contains trade patterns
inv_demand = inv_exog.merge(fcf_share,
                             left_on=['REG_imp', 'PROD_COMM'],
                             right_on=['REG_imp', 'TRAD_COMM'],
                             how='left')
inv_demand['dy'] = inv_demand['dk'] * inv_demand['FCF_share']

# 3. Convert to vector
dy_inv_exog = MRIO_df_to_vec(inv_demand, ...)
```

This applies proper trade patterns without INV_CONV conversion.

### Option 3: Custom INV_CONV (Less Recommended)

Replace the default 0.19964 diagonal with 1.0 diagonal:
- Sector N → 1.0 × Product N (perfect identity)
- Then fcf_share distributes properly

But this is a workaround - Options 1 or 2 are cleaner.

## Recommendation

**Use Option 1 (Final demand sheet)** because:

1. ✓ Matches your data structure exactly
2. ✓ No misleading column names ("Sector investing code*" when you mean products)
3. ✓ No unnecessary conversions
4. ✓ Official MINDSET feature for direct product specifications
5. ✓ Can specify trade flows explicitly if needed

## Next Steps

1. Examine "Final demand" sheet structure in MINDSET template
2. Convert one Strategy file to "Final demand" format
3. Test with RUN_ONE_SCENARIO.py using scenario.set_fd_exog()
4. Verify results are reasonable before batch processing

## Key Insight

You discovered that MINDSET's template shows products in "Sector investing code*" - this is likely because MINDSET's default INV_CONV is diagonal (identity-like). However, the 0.19964 scaling factor suggests this isn't the intended primary use case. The "Final demand" sheet is the proper way to directly specify products.
