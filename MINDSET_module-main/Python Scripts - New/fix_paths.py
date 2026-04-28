"""
Quick Path Fix for MINDSET Employment Tutorial
"""

import os
from pathlib import Path

# Get current working directory
cwd = Path(os.getcwd())
print(f"Current directory: {cwd}")

# Correct way to create output directory
# Option 1: In current directory
output_dir = cwd / "GLORIA_results"

# Option 2: In parent directory (MINDSET_module-main)
if cwd.name == "Python Scripts - New":
    output_dir = cwd.parent / "GLORIA_results"
else:
    output_dir = cwd / "GLORIA_results"

print(f"Output directory will be: {output_dir}")

# Try to create it
try:
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Successfully created: {output_dir}")
except PermissionError as e:
    print(f"✗ Permission error: {e}")
    print(f"\nTrying alternative location...")
    # Fallback: create in current directory
    output_dir = cwd / "GLORIA_results"
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Created in current directory: {output_dir}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test write permission
test_file = output_dir / "test.txt"
try:
    with open(test_file, 'w') as f:
        f.write("Test")
    test_file.unlink()  # Delete test file
    print(f"✓ Write permission confirmed")
except Exception as e:
    print(f"✗ Cannot write to directory: {e}")

print(f"\nUse this path in your script:")
print(f"output_dir = Path(r'{output_dir}')")
