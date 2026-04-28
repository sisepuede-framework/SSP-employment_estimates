"""
Delete the old (incorrectly dimensioned) L_BASE file before recalculating
"""
import os

# Path to the L_BASE file
l_base_path = "GLORIA_db\\v57\\2019\\parsed_db_original\\GLORIA_L_Base_2019.mat"

if os.path.exists(l_base_path):
    file_size_mb = os.path.getsize(l_base_path) / (1024 * 1024)
    print(f"Found L_BASE file: {file_size_mb:.1f} MB")
    print(f"Deleting old file...")
    os.remove(l_base_path)
    print(f"✓ Deleted successfully")
    print()
    print("You can now run CALCULATE_L_BASE_ONCE.py to create the correct file")
    print("Expected new file size: ~7 MB (960×960 matrix for 8 countries)")
else:
    print("L_BASE file not found - no need to delete")
    print("You can run CALCULATE_L_BASE_ONCE.py to create it")
