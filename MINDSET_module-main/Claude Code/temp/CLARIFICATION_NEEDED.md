# Clarification Needed: Strategy File Intent

Based on examining MINDSET's official template, I need to clarify your exact intent.

## MINDSET's Official Design (from template)

### "Investment by" Sheet Intent
The template example shows:
```
Italy | ITA | Basic aluminium | 78 | 0.12 | percentage
<< Increase investments BY the basic aluminium sector in Italy
```

**"Sector investing code*" = The SECTOR that is investing** (not what to buy)

The workflow is:
1. User specifies: "Sector 78 invests $X"
2. INV_CONV converts: "Sector 78 investing" → multiple products (construction, machinery, etc.)
3. fcf_share distributes: Products sourced from multiple countries

### Range Notation
Template supports ranges:
```
Germany | DEU | NaN | 1-23 | 1000 | absolute
<< 1000 kUSD in agricultural sectors (1-23)
```

Using "1-23" means: All sectors 1 through 23 invest (total $1000k split among them)

### Units Scale
Template comment: "1000 kUSD" means:
- File shows: 1000
- Units: kUSD (thousands of USD)
- Actual value: $1,000,000

## Your Strategy File Shows

### Individual Codes Listed
```
Growing wheat               | 1  | 20952.38
Growing maize               | 2  | 20952.38
Growing cereals             | 3  | 20952.38
...
Forestry and logging        | 21 | 20952.38
...
Computers                   | 90 | 42500.00
Machinery and equipment     | 86 | 42500.00
```

**You listed codes individually with specific amounts** (not using ranges)

## Three Critical Questions

### Question 1: Sector vs. Product Intent

When you wrote "90 | 42500", did you mean:

**A) SECTOR 90 (Computer manufacturing) invests $42.5M**
- This sector invests, INV_CONV converts to products they'd buy
- Following MINDSET's intended design
- Problem: INV_CONV redistributes your investment

**B) BUY PRODUCT 90 (Computers) for $42.5M**
- Direct purchase of computers as investment goods
- Not MINDSET's intended "Investment by" use
- This is what you told me: "specific products that would be purchased"

**Your earlier statement suggested (B)**: "The way I built the Strategy files, it's already a demand vector specifying the specific products that would be purchased in that strategy as if I was spending $1 million USD."

### Question 2: Why Individual Codes vs. Range?

Agricultural codes 1-21 are listed individually, each with 20952.38.

**If you meant sectors investing:**
- Why not use "1-21" range?
- Template shows ranges for sector groups

**If you meant products to buy:**
- Individual listing makes sense
- Each product gets specific allocation

### Question 3: Scale Verification

Your file shows values like 42500, 26000, 20952.38.

**Are these in kUSD (following MINDSET convention)?**
- 42500 in file = 42,500 kUSD = $42,500,000 actual
- Total ~1000 kUSD = $1,000,000 actual

**Or absolute USD?**
- 42500 in file = $42,500 actual
- Total = $1,000,000 actual

Based on MINDSET template, should be kUSD.

## Impact on Our Problem

### If Intent = (A) Sectors Investing
Then we need to understand:
- Why is INV_CONV redistributing "incorrectly"?
- What's the "correct" product distribution for each sector?
- Should we modify INV_CONV or accept its conversion logic?

### If Intent = (B) Direct Product Purchase
Then we need to:
- Use identity INV_CONV (Sector N → 100% Product N)
- Or switch to "Final demand" sheet (explicit products)
- Or create custom workflow bypassing investment module

## My Understanding Based on Our Conversation

Based on your statements:
1. "specific products that would be purchased"
2. "already a demand vector"
3. You chose "Investment by" to avoid specifying producing countries

**I believe you mean (B): Direct product purchase**

The codes are product codes, not investing sectors:
- Code 90 = Buy computers (Product 90)
- Code 1-21 = Buy agricultural products
- Code 86 = Buy machinery products

## Next Steps

**Please confirm:**
1. **Intent**: Are codes meant as products to buy (B) or sectors investing (A)?
2. **Scale**: Are values in kUSD (MINDSET standard) or absolute USD?
3. **Preference**: If (B), should we use identity INV_CONV or switch to Final demand sheet?

Once confirmed, I'll implement the correct solution.
