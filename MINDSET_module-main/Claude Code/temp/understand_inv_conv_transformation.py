"""
Understand how INV_CONV gets transformed from matrix to long format
"""
import sys
import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario

output_file = "Claude Code/temp/inv_conv_transformation.txt"

with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("Understanding INV_CONV Transformation\n")
    f.write("="*80 + "\n\n")

    try:
        # Load base data
        MRIO_BASE = exog_vars()

        f.write("STEP 1: INV_CONV as loaded from file\n")
        f.write("-"*80 + "\n")
        f.write(f"Type: {type(MRIO_BASE.INV_CONV)}\n")
        f.write(f"Shape: {MRIO_BASE.INV_CONV.shape}\n")
        f.write(f"Columns: {list(MRIO_BASE.INV_CONV.columns[:10])}...\n\n")
        f.write("First 5x5 block:\n")
        f.write(MRIO_BASE.INV_CONV.iloc[:5, :6].to_string() + "\n\n")

        # Check diagonal values
        diagonal_vals = []
        for i in range(min(10, 120)):
            col_name = str(i + 1)
            if col_name in MRIO_BASE.INV_CONV.columns:
                val = MRIO_BASE.INV_CONV.iloc[i, MRIO_BASE.INV_CONV.columns.get_loc(col_name)]
                diagonal_vals.append(val)

        f.write(f"First 10 diagonal values: {diagonal_vals}\n\n")

        # Now load a scenario to see how it transforms INV_CONV
        f.write("STEP 2: How scenario.set_inv_conv_adj() transforms it\n")
        f.write("-"*80 + "\n")

        class MockLog:
            def log_to_csv(self, *args, **kwargs): pass
            def log(self, *args, **kwargs): pass

        scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
        Scenario = scenario(MRIO_BASE, scenario_file, MockLog())

        # This transforms INV_CONV to long format
        INV_CONV_long = Scenario.set_inv_conv_adj(MRIO_BASE)

        f.write(f"After transformation:\n")
        f.write(f"Type: {type(INV_CONV_long)}\n")
        f.write(f"Shape: {INV_CONV_long.shape}\n")
        f.write(f"Columns: {list(INV_CONV_long.columns)}\n\n")
        f.write("First 20 rows:\n")
        f.write(INV_CONV_long.head(20).to_string() + "\n\n")

        # Check specific mappings
        f.write("STEP 3: Check specific sector→product mappings\n")
        f.write("-"*80 + "\n")
        for sector in [1, 55, 89, 90]:
            sector_data = INV_CONV_long[
                (INV_CONV_long['PROD_COMM'] == str(sector)) &
                (INV_CONV_long['REG_imp'] == 'MEX')
            ]
            f.write(f"\nSector {sector} in MEX invests in:\n")
            nonzero = sector_data[sector_data['input_coeff'] > 0].sort_values('input_coeff', ascending=False)
            if len(nonzero) > 0:
                f.write(nonzero[['TRAD_COMM', 'input_coeff']].head(10).to_string() + "\n")
            else:
                f.write("  No products (all zero)\n")

        f.write("\n" + "="*80 + "\n")
        f.write("SUCCESS\n")

    except Exception as e:
        f.write(f"\nERROR: {str(e)}\n")
        import traceback
        f.write(traceback.format_exc())

print(f"Output written to: {output_file}")
print("Please check the file to see INV_CONV structure")
