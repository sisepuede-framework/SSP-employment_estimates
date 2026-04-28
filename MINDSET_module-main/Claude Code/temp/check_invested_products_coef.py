"""
Check employment coefficients for the specific products being invested in
"""
import sys
import os
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.employment import empl

MRIO_BASE = exog_vars()
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

print("="*80)
print("EMPLOYMENT COEFFICIENTS FOR INVESTED PRODUCTS")
print("="*80)
print()

# Products being invested in: 86, 89, 90, 91, 65-70
invested_products = [65, 66, 67, 68, 69, 70, 86, 89, 90, 91]

print("Product coefficients for EGY vs MEX:")
print("-"*80)
print(f"{'Product':<10} {'EGY':>10} {'MEX':>10} {'Ratio (EGY/MEX)':>18}")
print("-"*80)

egy_total = 0
mex_total = 0

for prod in invested_products:
    egy_coef = Empl_model.EMPL_COEF[
        (Empl_model.EMPL_COEF['REG_imp'] == 'EGY') &
        (Empl_model.EMPL_COEF['PROD_COMM'] == prod)
    ]['empl_coef'].values[0]

    mex_coef = Empl_model.EMPL_COEF[
        (Empl_model.EMPL_COEF['REG_imp'] == 'MEX') &
        (Empl_model.EMPL_COEF['PROD_COMM'] == prod)
    ]['empl_coef'].values[0]

    ratio = egy_coef / mex_coef if mex_coef != 0 else float('inf')

    print(f"{prod:<10} {egy_coef:>10.6f} {mex_coef:>10.6f} {ratio:>18.2f}x")

    egy_total += egy_coef
    mex_total += mex_coef

print("-"*80)
avg_egy = egy_total / len(invested_products)
avg_mex = mex_total / len(invested_products)
avg_ratio = avg_egy / avg_mex if avg_mex != 0 else float('inf')

print(f"{'Average':<10} {avg_egy:>10.6f} {avg_mex:>10.6f} {avg_ratio:>18.2f}x")
print()

print("="*80)
print("COMBINED ANALYSIS")
print("="*80)
print()
print("1. Employment coefficient ratio (for these products): {:.2f}x".format(avg_ratio))
print("2. Baseline intensity ratio (from LABOR_BASE/q_base): 2.72x")
print("3. Expected combined ratio: {:.2f}x".format(avg_ratio * 2.72))
print("4. Observed ratio in test results: 8.6x")
print()

if abs(avg_ratio * 2.72 - 8.6) < 1.0:
    print("[OK] The employment coefficients explain the difference!")
else:
    print("[WARNING] There may be other factors at play")
