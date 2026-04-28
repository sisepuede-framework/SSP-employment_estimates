"""
Check if build_A_base works
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("Step 1: Import modules")
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("Step 2: Load MRIO")
MRIO_BASE = exog_vars()

print("Step 3: Initialize IO")
IO_model = IO(MRIO_BASE)

print(f"Step 4: Check DIMS = {IO_model.DIMS}")
print(f"Step 5: Check R_list length = {len(IO_model.R_list)}")
print(f"Step 6: Check P_list length = {len(IO_model.P_list)}")

print("Step 7: Call build_A_base()")
IO_model.build_A_base()

print(f"Step 8: Check A_BASE shape = {IO_model.A_BASE.shape}")
print(f"Step 9: Check A_BASE type = {type(IO_model.A_BASE)}")

print("SUCCESS")
