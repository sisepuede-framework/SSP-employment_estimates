"""
Find where Y_BASE.mat was actually saved
"""
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Looking for GLORIA_Y_Base_2019.mat files")
print("="*80)

base_dir = "GLORIA_db/v57/2019"

print(f"\nSearching in: {base_dir}")
print("-"*80)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if "GLORIA_Y_Base" in file and file.endswith(".mat"):
            full_path = os.path.join(root, file)
            size_kb = os.path.getsize(full_path) / 1024
            print(f"✓ Found: {full_path}")
            print(f"  Size: {size_kb:.1f} KB")

# Also check if SSP folder exists
ssp_folder = os.path.join(base_dir, "SSP")
if os.path.exists(ssp_folder):
    print(f"\n✓ SSP folder exists: {ssp_folder}")
    print(f"  Contents:")
    for item in os.listdir(ssp_folder):
        print(f"    {item}")
else:
    print(f"\n✗ SSP folder does NOT exist: {ssp_folder}")
