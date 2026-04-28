"""
Find all *_Base*.mat files and check their locations
"""
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Finding all *_Base*.mat files")
print("="*80)

base_dir = "GLORIA_db/v57/2019"

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if "_Base_" in file and file.endswith(".mat"):
            full_path = os.path.join(root, file)
            size_kb = os.path.getsize(full_path) / 1024
            print(f"\n{file}:")
            print(f"  Location: {full_path}")
            print(f"  Size: {size_kb:.1f} KB")

print("\n" + "="*80)
print("What Variable_list_MINDSET_SSP.xlsx expects:")
print("="*80)
print("\nL_BASE: GLORIA_db\\v57\\2019\\SSP\\GLORIA_L_Base_2019.mat")
print("G_BASE: GLORIA_db\\v57\\2019\\SSP\\GLORIA_G_Base_2019.mat")
print("Y_BASE: GLORIA_db\\v57\\2019\\SSP\\GLORIA_Y_Base_2019.mat")

print("\n" + "="*80)
print("ACTION NEEDED:")
print("="*80)
print("\nMove these files to SSP folder:")
print('  move "GLORIA_db\\v57\\2019\\GLORIA_L_Base_2019.mat" "GLORIA_db\\v57\\2019\\SSP\\"')
print('  move "GLORIA_db\\v57\\2019\\GLORIA_G_Base_2019.mat" "GLORIA_db\\v57\\2019\\SSP\\"')
