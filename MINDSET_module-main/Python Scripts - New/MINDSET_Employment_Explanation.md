# MINDSET EMPLOYMENT MODULE - DETAILED EXPLANATION

## Author: Fernando Esteves
## Date: March 2026

---

## **KEY DIFFERENCES: My Simplified Approach vs. MINDSET**

### **My Simplified Approach (What I did):**
```python
# Simple linear relationship
delta_employment = employment_coef * delta_x
```

**Problems:**
- ❌ Doesn't normalize by baseline employment intensity
- ❌ Can't decompose by effect type (tech, trade, household, etc.)
- ❌ Not the actual MINDSET methodology

---

### **MINDSET Actual Approach:**

```python
# Step 1: Calculate employment multiplier
empl_multiplier = empl_coef * (empl_base / q_base)

# Step 2: Calculate employment change
dempl = empl_multiplier * dq
```

**Advantages:**
- ✅ Normalizes by baseline employment-to-output ratio
- ✅ Can decompose into multiple effect types
- ✅ More accurate representation of employment dynamics

---

## **MINDSET EMPLOYMENT WORKFLOW (from RunMINDSET.py)**

### **STEP 1: Initialize Employment Module (line 498-501)**
```python
# Import employment module
from SourceCode.employment import empl

# Create employment model instance
Empl_model = empl(MRIO_BASE)

# Build employment coefficients (processes GLORIA data)
Empl_model.build_empl_coef()

# Calculate employment multipliers
Empl_model.calc_empl_multiplier(
    empl_base,  # Baseline employment by sector/country
    q_base      # Baseline gross output by sector/country
)
```

**What happens in `calc_empl_multiplier`:**
```python
empl_coef = employment coefficient from data (workers per $ output)
empl_base = baseline employment (workers)
q_base = baseline output ($)

empl_multiplier = empl_coef * (empl_base / q_base)
```

**Why normalize by (empl_base / q_base)?**
- Captures actual employment intensity in baseline
- Accounts for productivity differences across sectors/countries
- More accurate than using raw coefficients

---

### **STEP 2: Calculate Output Changes (line 508-509)**
```python
# Total output change from ALL effects
dq_total = (
    dq_IO_eff +           # Technology/energy effects
    dq_hh_price +         # Household price effects
    dq_hh_inc +           # Household income effects
    dq_gov_recyc +        # Government recycling
    dq_inv_induced +      # Induced investment
    dq_inv_recyc +        # Investment recycling
    dq_inv_exog +         # Exogenous investment
    dq_hh_exog_fd +       # Exogenous household demand
    dq_fcf_exog_fd +      # Exogenous capital formation
    dq_gov_exog_fd +      # Exogenous government demand
    dq_supply_constraint  # Supply constraints
)
```

---

### **STEP 3: Calculate Employment Changes by Effect Type (line 511-516)**
```python
# Calculate employment for each effect type
[dempl_total,           # Total employment change
 dempl_tech_eff,        # From technology/energy substitution
 dempl_trade_eff,       # From trade effects
 dempl_hh_price,        # From household price changes
 dempl_hh_inc,          # From household income changes
 dempl_gov_recyc,       # From government spending
 dempl_inv_induced,     # From induced investment
 dempl_inv_recyc,       # From investment recycling
 dempl_inv_exog,        # From exogenous investment
 dempl_hh_exog_fd,      # From exogenous household demand
 dempl_fcf_exog_fd,     # From exogenous capital formation
 dempl_gov_exog_fd,     # From exogenous government demand
 dempl_supply_constraint # From supply constraints
] = Empl_model.calc_dempl([
    dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price,
    dq_hh_inc, dq_gov_recyc, dq_inv_induced, dq_inv_recyc,
    dq_inv_exog, dq_hh_exog_fd, dq_fcf_exog_fd,
    dq_gov_exog_fd, dq_supply_constraint
])
```

**What `calc_dempl` does:**
```python
def calc_dempl(self, dq):
    if type(dq) != list:
        # Single output change
        dempl = self.empl_multiplier * dq
        return dempl
    else:
        # Multiple output changes (different effects)
        dempl = {}
        for i in range(len(dq)):
            dempl_i = self.empl_multiplier * dq[i]
            dempl[i] = dempl_i
        return dempl.values()
```

---

## **COMPARISON: Simple vs. MINDSET Approach**

### **Numerical Example:**

**Given:**
- `empl_coef` = 100 workers/$M (from data)
- `empl_base` = 50,000 workers (baseline employment)
- `q_base` = $1,000M (baseline output)
- `delta_x` = $10M (output increase)

**My Simplified Approach:**
```python
delta_employment = 100 * 10 = 1,000 workers
```

**MINDSET Approach:**
```python
empl_multiplier = 100 * (50,000 / 1,000) = 5,000
delta_employment = 5,000 * 10 = 50,000 workers  # VERY DIFFERENT!
```

**Wait, that seems wrong!** Let me recalculate...

Actually, the formula should be:
```python
# empl_multiplier is workers per $ of OUTPUT CHANGE
empl_multiplier = empl_coef * (empl_base / q_base)

# But empl_coef is already workers per $ output
# So (empl_base / q_base) is workers per $ in baseline
# This normalizes the coefficient

# More accurate interpretation:
employment_intensity = empl_base / q_base = 50 workers/$M
empl_multiplier = empl_coef * employment_intensity

# If empl_coef = 100 and employment_intensity = 50:
# This doesn't make dimensional sense...
```

**Let me re-examine the code more carefully:**

Looking at line 40-41 in employment.py:
```python
self.empl_multiplier = empl_coef * (np.divide(
    empl_base, q_base, out=np.zeros_like(empl_base), where=q_base!=0))
```

**Dimensional Analysis:**
- `empl_coef`: elasticity (% change employment / % change output)
- `empl_base`: workers
- `q_base`: $ million
- `empl_base / q_base`: workers/$M (employment intensity)

So:
```
empl_multiplier = elasticity * (workers/$M)
               = (% Δempl / % Δoutput) * (workers/$M)

When applied to dq ($M change):
dempl = empl_multiplier * dq
     = elasticity * (workers/$M) * ($M)
     = elasticity * workers
```

**This suggests empl_coef is an ELASTICITY, not a direct coefficient!**

---

## **KEY INSIGHT:**

MINDSET employment coefficients are **ELASTICITIES** (percentage changes), not direct workers-per-dollar coefficients!

The formula:
```python
empl_multiplier = empl_coef * (empl_base / q_base)
```

Converts elasticities to absolute employment changes per dollar of output change.

---

## **FOR YOUR SYNTHETIC MODEL:**

We need to:

1. **Define properly:**
   - `empl_base`: Baseline employment by sector (workers)
   - `q_base`: Baseline output by sector ($M)
   - `empl_coef`: Employment-output elasticity (often ~0.3 to 0.8)

2. **Calculate multiplier:**
   ```python
   empl_multiplier = empl_coef * (empl_base / q_base)
   ```

3. **Calculate employment change:**
   ```python
   dempl = empl_multiplier * delta_x
   ```

---

## **QUESTIONS FOR YOU:**

1. **Employment Coefficients in Your Model:**
   - Should we use **elasticities** (MINDSET approach)?
   - Or **direct coefficients** (workers/$M)?
   - For synthetic model, direct coefficients might be clearer for teaching

2. **Decomposition:**
   - Do you want to track employment by effect type?
   - Or just total employment change?

3. **Adaptation Level:**
   - Exact MINDSET class structure (with MRIO_BASE)?
   - Or simplified version that follows MINDSET logic?

---

## **MY RECOMMENDATION FOR NEXT STEP:**

Create **two versions** of employment calculation:

### **Version A: Simple Direct Coefficients (for teaching)**
```python
# Easy to understand
employment_coef = [280, 95, 150, 220, 50]  # workers/$M
dempl = employment_coef * delta_x
```

### **Version B: MINDSET-style with Elasticities (for accuracy)**
```python
# More accurate, follows MINDSET
empl_elasticity = [0.7, 0.6, 0.75, 0.65, 0.5]  # elasticity
empl_base = [1,400,761, 404,230, ...]           # baseline workers
q_base = [5,002.72, 4,255.05, ...]              # baseline output $M

empl_multiplier = empl_elasticity * (empl_base / q_base)
dempl = empl_multiplier * delta_x
```

**Which approach do you prefer for your analysis?**

---

## **NEXT STEPS:**

Once you answer these questions, I'll:
1. Create adapted MINDSET employment module for 5-sector model
2. Implement your transformation vector system
3. Build complete analysis script

**Ready to proceed?**
