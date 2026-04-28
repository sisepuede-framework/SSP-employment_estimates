"""
Check if LABOR_BASE aggregation matches q_base from L_BASE and Y_BASE
"""
import sys
import os
import numpy as np
import pandas as pd
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO
from SourceCode.utils import MRIO_df_to_vec

print("="*80)
print("CHECKING LABOR_BASE vs q_base CONSISTENCY")
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

empl_base = MRIO_df_to_vec(
    empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
    "REG_imp", "PROD_COMM", "vol_total",
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print("TOTAL ECONOMY-WIDE CHECK:")
print("-"*80)

country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}

for country in ['ROW', 'BGR', 'BLZ', 'EGY', 'LBY', 'MAR', 'MEX', 'UGA']:
    idx = country_idx[country]
    start_idx = idx * 120
    end_idx = start_idx + 120

    country_empl = empl_base[start_idx:end_idx].sum()
    country_output = IO_model.q_base[start_idx:end_idx].sum()
    intensity = country_empl / country_output if country_output > 0 else 0

    print(f"{country}:")
    print(f"  Total employment: {country_empl:>15,.0f} workers")
    print(f"  Total output:     {country_output:>15,.0f} kUSD")
    print(f"  Intensity:        {intensity:>15.4f} workers/kUSD = {intensity*1000:>8.1f} workers/$M")
    print()

print("="*80)
print("SANITY CHECK: Compare to real-world data")
print("="*80)
print()
print("Expected employment intensities (workers per $M GDP):")
print("  Developed economies (like ROW/China): 5-15")
print("  Middle-income (like MEX, BGR, MAR, EGY): 15-40")
print("  Low-income (like BLZ, UGA): 40-100")
print("  Very poor (like LBY): could be higher")
print()

print("If numbers are MUCH higher (>200), LABOR_BASE might not be aggregated correctly")
print("If numbers are MUCH lower (<5), q_base might not be aggregated correctly")
print()

print("="*80)
print("CHECK: Where do these files come from?")
print("="*80)
print()
print("LABOR_BASE: GLORIA_db/v57/2019/SSP/labor_data.pkl")
print("L_BASE: GLORIA_db/v57/2019/SSP/GLORIA_L_Base_2019.mat")
print("Y_BASE: GLORIA_db/v57/2019/SSP/GLORIA_Y_Base_2019.mat")
print()
print("These files need to be aggregated CONSISTENTLY from the 164-country")
print("GLORIA data. If one is aggregated differently, the employment intensities")
print("will be nonsensical.")
