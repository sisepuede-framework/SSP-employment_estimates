"""
Diagnose why EGY has 8.6x higher labor intensity than MEX
"""
import sys
import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO
from SourceCode.employment import empl

print("="*80)
print("DIAGNOSING EMPLOYMENT DISCREPANCY: EGY vs MEX")
print("="*80)
print()

# Load data
MRIO_BASE = exog_vars()
IO_model = IO(MRIO_BASE)
IO_model.initialize()

# Calculate employment baseline
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]

print("STEP 1: Check LABOR_BASE data")
print("-"*80)
for country in ['EGY', 'MEX']:
    country_empl = empl_base_df[empl_base_df['REG_imp'] == country]['vol_total'].sum()
    print(f"{country} total employment: {country_empl:,.0f} workers")
print()

print("STEP 2: Check baseline output (q_base)")
print("-"*80)
country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}
for country in ['EGY', 'MEX']:
    idx = country_idx[country]
    start_idx = idx * 120
    end_idx = start_idx + 120
    country_output = IO_model.q_base[start_idx:end_idx].sum()
    print(f"{country} baseline output: ${country_output:,.0f} kUSD")
print()

print("STEP 3: Employment intensity (workers per kUSD output)")
print("-"*80)
for country in ['EGY', 'MEX']:
    idx = country_idx[country]
    start_idx = idx * 120
    end_idx = start_idx + 120
    country_empl = empl_base_df[empl_base_df['REG_imp'] == country]['vol_total'].sum()
    country_output = IO_model.q_base[start_idx:end_idx].sum()
    intensity = country_empl / country_output if country_output > 0 else 0
    print(f"{country}: {intensity:.4f} workers/kUSD = {intensity*1000:.1f} workers/$M")
print()

print("STEP 4: Check employment coefficients by product")
print("-"*80)
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

# Show employment coefficients for a few products in each country
print("Sample products (10, 50, 90) employment coefficients:")
print()
for prod in [10, 50, 90]:
    print(f"Product {prod}:")
    for country in ['EGY', 'MEX']:
        idx = country_idx[country]
        prod_idx = idx * 120 + (prod - 1)
        empl_coef = Empl_model.empl_coef[prod_idx] if hasattr(Empl_model, 'empl_coef') else 0
        print(f"  {country}: {empl_coef:.6f}")
    print()

print("STEP 5: Check what products are being invested in")
print("-"*80)
from SourceCode.scenario import scenario

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

for country in ['EGY', 'MEX']:
    scenario_file = f"GLORIA_template/Scenarios/Strategy_1004_{country}.xlsx"
    Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
    Scenario.set_exog_inv()

    print(f"{country} investments:")
    inv_products = Scenario.inv_exog[Scenario.inv_exog['dk'] > 0][['PROD_COMM', 'dk']].sort_values('dk', ascending=False).head(10)
    print(inv_products.to_string(index=False))
    print()

print("="*80)
print("ANALYSIS")
print("="*80)
print()
print("Check if:")
print("1. LABOR_BASE data is correct for both countries")
print("2. Baseline output (q_base) is reasonable")
print("3. Employment intensity differences are realistic")
print("4. Product mix affects results (labor-intensive vs capital-intensive)")
