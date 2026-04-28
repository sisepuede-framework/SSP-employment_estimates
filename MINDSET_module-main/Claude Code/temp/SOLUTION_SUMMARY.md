# SOLUTION: Fix INV_CONV for Investment by Sheet

## The Root Cause (CONFIRMED)

INV_CONV is NOT a simple diagonal matrix. It's a complex conversion matrix that redistributes each sector's investment across multiple products based on empirical investment patterns.

**Example from your data:**
- When you put $42,500 in "Sector 90":
  - 45.33% → Product 86 ($19,265)
  - 11.46% → Product 101 ($4,871)
  - Only 4.63% → Product 90 itself ($1,968)
  - And 10 more products get shares!

This is why:
- Product 86 got overloaded (receives from sectors 55, 89, 90)
- Products 89 got ZERO (sector 89 doesn't fund product 89)
- Results had -0.0127 correlation with intended investment

## The Solution

**Replace INV_CONV with a TRUE identity matrix** where:
- Sector N → 100% to Product N
- Sector N → 0% to all other products

This makes "Sector investing code*" work correctly when you put product codes there.

## Implementation Steps

### ✓ Step 1: Create Identity Matrix (DONE)

I've created: `GLORIA_db/v57/2019/SSP/INV_CONV.xlsx`
- 120×120 identity matrix
- Diagonal = 1.0
- Off-diagonal = 0.0

### Step 2: Update Variable_list_MINDSET_SSP.xlsx

Add or update the INV_CONV entry:

| Variable name | Path | Type |
|---------------|------|------|
| INV_CONV | GLORIA_db\v57\2019\SSP\INV_CONV.xlsx | DataFrame |

**How to do this:**
1. Open `GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx`
2. Add a new row (or update existing INV_CONV row)
3. Fill in the three columns as shown above
4. Save the file

### Step 3: Test the Fix

Run the test script to verify results are now reasonable:

```bash
python "Claude Code/temp/TEST_FIXED_INV_CONV.py"
```

This will:
- Load the new identity INV_CONV
- Run Strategy_1004_MEX
- Check if investment is preserved (should be ~100%)
- Check if employment estimates are reasonable
- Show results by country

### Expected Results After Fix

**Before fix:**
- Investment input: $1,000,000
- After INV_CONV: ~$200,000 (80% loss)
- Wrong product distribution (correlation -0.0127)

**After fix:**
- Investment input: $1,000,000
- After INV_CONV: ~$1,000,000 (preserved)
- Correct product distribution (correlation ≈1.0)
- fcf_share distributes across countries (economically realistic)

## Important Note on fcf_share

Even with identity INV_CONV, the investment will still be distributed across countries using fcf_share. This is CORRECT behavior:

**Example:**
- You invest $10,000 in Product 55 (Machinery) in MEX
- fcf_share shows MEX imports 30% of machinery
- Result:
  - $7,000 demand for MEX machinery (domestic)
  - $3,000 demand for ROW machinery (imports)

This is economically realistic - not all products are produced domestically.

## Alternative: If You Want Purely Domestic

If you want to force all investment to be domestic (no imports), you would need to:
1. Use the identity INV_CONV (Step 1-2 above)
2. ALSO modify fcf_share to be 100% domestic for each country

But this is unrealistic for most products. Better to let fcf_share reflect actual trade patterns.

## Files Created

1. `GLORIA_db/v57/2019/SSP/INV_CONV.xlsx` - Identity matrix
2. `Claude Code/temp/TEST_FIXED_INV_CONV.py` - Test script
3. `Claude Code/temp/key_sectors_conversion.txt` - Diagnosis showing conversion patterns
4. `Claude Code/temp/INVESTMENT_MODULE_FINDINGS.md` - Detailed analysis
5. `Claude Code/temp/FIX_INVESTMENT_BY_APPROACH.md` - Fix strategies

## Next Action

**Please update Variable_list_MINDSET_SSP.xlsx** to add the INV_CONV entry, then let me know so we can run the test.
