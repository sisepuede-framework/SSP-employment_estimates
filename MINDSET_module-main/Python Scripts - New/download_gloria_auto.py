"""
================================================================================
GLORIA DATA DOWNLOADER - AUTOMATIC VERSION
================================================================================

This script automatically downloads GLORIA data without interactive prompts.
Pre-configured to download: Version 57, Year 2019 (recommended)

Author: Fernando Esteves
Date: March 2026
================================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime

print("="*80)
print("GLORIA MRIO DATABASE DOWNLOADER - AUTOMATIC MODE")
print("="*80)
print("\nAutomatically downloading GLORIA v57, year 2019...")

# =============================================================================
# STEP 1: CHECK AND INSTALL PYMRIO
# =============================================================================

print("\n" + "-"*80)
print("Step 1: Checking pymrio installation")
print("-"*80)

try:
    import pymrio
    print(f"✓ pymrio is installed (version {pymrio.__version__})")
except ImportError:
    print("✗ pymrio is NOT installed")
    print("\nAttempting automatic installation...")

    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymrio"],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print("✓ pymrio installed successfully!")
        import pymrio
        print(f"✓ pymrio version {pymrio.__version__} ready")
    except Exception as e:
        print(f"\n✗ Automatic installation failed: {e}")
        print("\nPlease install manually: pip install pymrio")
        sys.exit(1)

# =============================================================================
# STEP 2: SETUP PATHS
# =============================================================================

print("\n" + "-"*80)
print("Step 2: Setting up download paths")
print("-"*80)

# Get directories
cwd = Path(os.getcwd())
parent_dir = cwd.parent if cwd.name == "Python Scripts - New" else cwd

# Configure download
VERSION = 57
YEAR = 2019
gloria_folder = parent_dir / "GLORIA_db" / f"v{VERSION}" / str(YEAR) / "raw_download"

print(f"Current directory: {cwd}")
print(f"Parent directory: {parent_dir}")
print(f"Download destination: {gloria_folder}")
print(f"\nDownload configuration:")
print(f"  Version: {VERSION}")
print(f"  Year: {YEAR}")
print(f"  Size: ~250 MB")
print(f"  Time: ~5-15 minutes")

# Create folder
gloria_folder.mkdir(parents=True, exist_ok=True)
print(f"\n✓ Download folder created")

# =============================================================================
# STEP 3: CHECK EXISTING DATA
# =============================================================================

print("\n" + "-"*80)
print("Step 3: Checking for existing data")
print("-"*80)

existing_files = list(gloria_folder.glob("GLORIA_MRIOs_*.zip")) + \
                list(gloria_folder.glob("download_log.json"))

if existing_files:
    print(f"\n⚠ Found {len(existing_files)} existing file(s):")
    for f in existing_files[:5]:
        print(f"   - {f.name}")
    print("\nSkipping download (data already exists)")
    print("\nTo re-download, delete the folder:")
    print(f"   {gloria_folder}")
    sys.exit(0)
else:
    print("✓ No existing data found, proceeding with download")

# =============================================================================
# STEP 4: DOWNLOAD GLORIA DATA
# =============================================================================

print("\n" + "="*80)
print("DOWNLOADING GLORIA DATA")
print("="*80)
print(f"\nDownloading Version {VERSION}, Year {YEAR}...")
print("This will take 5-15 minutes. Please wait...")
print("(Monitor your internet connection to see progress)")

start_time = datetime.now()
print(f"\nStart time: {start_time.strftime('%H:%M:%S')}")

try:
    # Download using pymrio
    gloria_log = pymrio.download_gloria(
        storage_folder=str(gloria_folder),
        year=YEAR,
        version=VERSION
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n{'='*80}")
    print("✓ DOWNLOAD COMPLETED SUCCESSFULLY!")
    print(f"{'='*80}")
    print(f"Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")

    # Save download info
    info_file = gloria_folder / "download_info.txt"
    with open(info_file, 'w') as f:
        f.write(f"GLORIA Download Information\n")
        f.write(f"="*60 + "\n")
        f.write(f"Version: {VERSION}\n")
        f.write(f"Year: {YEAR}\n")
        f.write(f"Download date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)\n")
        f.write(f"Folder: {gloria_folder}\n")
        f.write(f"\nDownload log:\n")
        f.write(str(gloria_log))

    print(f"\nDownload info saved: {info_file.name}")

    # Check downloaded files
    downloaded_files = list(gloria_folder.glob("*"))
    total_size = sum(f.stat().st_size for f in downloaded_files if f.is_file())

    print(f"\nDownloaded files: {len(downloaded_files)}")
    print(f"Total size: {total_size / (1024**2):.1f} MB")

    print("\nFirst 10 files:")
    for file in downloaded_files[:10]:
        if file.is_file():
            size_mb = file.stat().st_size / (1024**2)
            print(f"  - {file.name} ({size_mb:.1f} MB)")
    if len(downloaded_files) > 10:
        print(f"  ... and {len(downloaded_files) - 10} more files")

    # Save summary
    summary_file = parent_dir / "GLORIA_db" / "download_summary.txt"
    with open(summary_file, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"Download: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Version {VERSION}, Year {YEAR}: SUCCESS\n")
        f.write(f"Duration: {duration:.0f}s, Size: {total_size / (1024**2):.1f} MB\n")
        f.write(f"Location: {gloria_folder}\n")

    print(f"\nSummary appended to: {summary_file.name}")

    # =============================================================================
    # NEXT STEPS
    # =============================================================================

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
✓ GLORIA data downloaded successfully!

WHAT TO DO NEXT:

1. PARSE THE DATA
   The downloaded data needs to be parsed for MINDSET.

   Option A - Use pymrio (simpler):
   >>> import pymrio
   >>> gloria = pymrio.parse_gloria(path=str(gloria_folder.parent))
   >>> gloria.calc_all()

   Option B - Use MINDSET parsing scripts:
   >>> python ParseCode/Parsing-Gloria-mat.py
   >>> python ParseCode/Parsing-Gloria-pkl.py

2. RUN THE TUTORIAL
   Now you can analyze Uganda employment impacts:
   >>> python "Python Scripts - New/uganda_employment_impact_tutorial.py"

3. VERIFY THE DATA
   Quick verification:
   >>> import pymrio
   >>> gloria = pymrio.parse_gloria(path='GLORIA_db/v57/2019')
   >>> print(f"Countries: {len(gloria.get_regions())}")
   >>> print(f"Sectors: {len(gloria.get_sectors())}")
   >>> print("UGA" in gloria.get_regions())  # Should be True

4. USE WITH MINDSET
   Full model run:
   >>> python RunMINDSET.py
    """)

    print("\n" + "="*80)
    print("DOWNLOAD COMPLETE - READY FOR ANALYSIS!")
    print("="*80)

except Exception as e:
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n{'='*80}")
    print("✗ DOWNLOAD FAILED")
    print(f"{'='*80}")
    print(f"Duration before failure: {duration:.0f} seconds")
    print(f"Error: {str(e)}")

    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Verify disk space (need ~500 MB)")
    print("3. Try manual download: https://www.gloria-mrio.com/")
    print("4. Check firewall/proxy settings")

    # Save error log
    error_file = gloria_folder / "download_error.txt"
    with open(error_file, 'w') as f:
        f.write(f"Download failed at {datetime.now()}\n")
        f.write(f"Error: {str(e)}\n")

    sys.exit(1)
