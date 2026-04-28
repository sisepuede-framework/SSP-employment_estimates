"""
Check structure of L_BASE, G_BASE, and Y_BASE .mat files in SSP folder
"""
import scipy.io
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Check .mat file structures in SSP folder")
print("="*80)

mat_files = {
    'L_BASE': 'GLORIA_db/v57/2019/SSP/GLORIA_L_Base_2019.mat',
    'G_BASE': 'GLORIA_db/v57/2019/SSP/GLORIA_G_Base_2019.mat',
    'Y_BASE': 'GLORIA_db/v57/2019/SSP/GLORIA_Y_Base_2019.mat'
}

for name, path in mat_files.items():
    print(f"\n{name}: {path}")
    print("-"*80)

    if os.path.exists(path):
        print(f"✓ File exists ({os.path.getsize(path)/1024:.1f} KB)")

        try:
            mat_data = scipy.io.loadmat(path)
            print(f"  Keys: {list(mat_data.keys())}")

            # Show structure of data keys (non-metadata keys)
            for key in mat_data.keys():
                if not key.startswith('__'):
                    data = mat_data[key]
                    print(f"    {key}: type={type(data).__name__}, shape={data.shape if hasattr(data, 'shape') else 'N/A'}")

        except Exception as e:
            print(f"  ✗ Error loading: {e}")
    else:
        print(f"✗ File not found")

print("\n" + "="*80)
print("What InputOutput.py expects:")
print("="*80)
print("\nL_BASE.mat should contain:")
print("  Key: 'L_base' → (960, 960) array")
print("\nG_BASE.mat should contain:")
print("  Key: 'G_base' → (960, 960) array")
print("\nY_BASE.mat should contain:")
print("  Keys: 'y0', 'y_hh0', 'y_gov0', 'y_fcf0', 'y_npish', 'y_inv'")
print("  Each: (960,) or (960, 1) array")
