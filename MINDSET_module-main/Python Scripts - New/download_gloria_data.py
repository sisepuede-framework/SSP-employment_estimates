"""
================================================================================
GLORIA DATA DOWNLOADER
================================================================================

This script downloads GLORIA (Global Resource Input-Output Assessment) data
which is needed for the MINDSET employment impact model.

GLORIA Database:
- 169 countries
- 120 economic sectors per country
- Multi-Regional Input-Output tables
- Years available: 2000-2022
- Version 57 (latest stable as of 2024)

Author: Fernando Esteves
Date: March 2026
================================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime

print("="*80)
print("GLORIA MRIO DATABASE DOWNLOADER")
print("="*80)
print("\nThis script will download GLORIA data for use with the MINDSET model.")

# =============================================================================
# STEP 1: CHECK PYMRIO INSTALLATION
# =============================================================================

print("\n" + "-"*80)
print("Step 1: Checking pymrio installation")
print("-"*80)

try:
    import pymrio
    print(f"✓ pymrio is installed (version {pymrio.__version__})")
    PYMRIO_AVAILABLE = True
except ImportError:
    print("✗ pymrio is NOT installed")
    print("\npymrio is required to download GLORIA data.")
    print("\nTo install pymrio, run:")
    print("    pip install pymrio")

    install_now = input("\nWould you like to try installing pymrio now? (y/n): ")

    if install_now.lower() == 'y':
        print("\nAttempting to install pymrio...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pymrio"])
            print("\n✓ pymrio installed successfully!")
            print("Importing pymrio...")
            import pymrio
            print(f"✓ pymrio version {pymrio.__version__} ready to use")
            PYMRIO_AVAILABLE = True
        except Exception as e:
            print(f"\n✗ Installation failed: {e}")
            print("\nPlease install manually:")
            print("    pip install pymrio")
            print("\nThen run this script again.")
            sys.exit(1)
    else:
        print("\nExiting. Please install pymrio and run this script again.")
        sys.exit(1)

# =============================================================================
# STEP 2: SETUP DOWNLOAD PARAMETERS
# =============================================================================

print("\n" + "-"*80)
print("Step 2: Configure download parameters")
print("-"*80)

print("""
GLORIA versions and years available:
- Versions: 53, 54, 55, 56, 57 (57 is latest stable)
- Years: 2000-2022 (depending on version)
- Recommended: Version 57, Year 2019 (most recent pre-COVID with complete data)

File size: ~200-300 MB compressed per year
Download time: 5-15 minutes (depending on internet speed)
""")

# Get current working directory
cwd = Path(os.getcwd())
print(f"Current directory: {cwd}")

# Navigate to parent directory (MINDSET_module-main folder)
# The script is in "Python Scripts - New", we want to put data in parent/GLORIA_db
parent_dir = cwd.parent if cwd.name == "Python Scripts - New" else cwd

# Ask user for download preferences
print("\n" + "="*60)
print("DOWNLOAD OPTIONS:")
print("="*60)
print("1. Download recommended (Version 57, Year 2019) - RECOMMENDED")
print("2. Download specific version/year")
print("3. Download multiple years")
print("4. Check existing downloads and exit")

choice = input("\nEnter choice (1-4): ").strip()

if choice == '4':
    # Check existing downloads
    print("\n" + "-"*80)
    print("Checking for existing GLORIA data...")
    print("-"*80)

    gloria_base = parent_dir / "GLORIA_db"
    if gloria_base.exists():
        print(f"\n✓ GLORIA_db folder exists: {gloria_base}")

        # Look for downloaded files
        downloaded_files = []
        for version_dir in gloria_base.glob("v*"):
            for year_dir in version_dir.glob("*"):
                if year_dir.is_dir():
                    # Check for GLORIA files
                    gloria_files = list(year_dir.rglob("GLORIA_MRIOs_*.zip")) + \
                                   list(year_dir.rglob("GLORIA_MRIOs_*.csv")) + \
                                   list(year_dir.rglob("download_log.json"))
                    if gloria_files:
                        downloaded_files.append((version_dir.name, year_dir.name, len(gloria_files)))

        if downloaded_files:
            print(f"\n✓ Found {len(downloaded_files)} existing download(s):")
            for version, year, file_count in downloaded_files:
                print(f"   - {version}/{year}: {file_count} files")
        else:
            print("\n✗ No GLORIA data files found in GLORIA_db folder")
    else:
        print(f"\n✗ GLORIA_db folder does not exist: {gloria_base}")

    print("\nExiting without downloading.")
    sys.exit(0)

elif choice == '1':
    # Recommended download
    downloads = [(57, 2019)]
    print("\n✓ Will download: Version 57, Year 2019")

elif choice == '2':
    # Custom single download
    print("\nEnter custom parameters:")
    try:
        version = int(input("  Version (53-57, recommended=57): ").strip() or "57")
        year = int(input("  Year (2000-2022, recommended=2019): ").strip() or "2019")

        if version < 53 or version > 57:
            print(f"⚠ Warning: Version {version} may not be available")
        if year < 2000 or year > 2022:
            print(f"⚠ Warning: Year {year} may not be available")

        downloads = [(version, year)]
        print(f"\n✓ Will download: Version {version}, Year {year}")
    except ValueError:
        print("\n✗ Invalid input. Exiting.")
        sys.exit(1)

elif choice == '3':
    # Multiple years
    print("\nEnter parameters for multiple years:")
    try:
        version = int(input("  Version (53-57, recommended=57): ").strip() or "57")
        year_start = int(input("  Start year (e.g., 2015): ").strip())
        year_end = int(input("  End year (e.g., 2019): ").strip())

        if year_start > year_end:
            print("\n✗ Start year must be <= end year. Exiting.")
            sys.exit(1)

        downloads = [(version, year) for year in range(year_start, year_end + 1)]
        print(f"\n✓ Will download: Version {version}, Years {year_start}-{year_end}")
        print(f"   Total downloads: {len(downloads)}")
        print(f"   Estimated time: {len(downloads) * 10} minutes")
        print(f"   Estimated size: {len(downloads) * 250} MB")
    except ValueError:
        print("\n✗ Invalid input. Exiting.")
        sys.exit(1)

else:
    print("\n✗ Invalid choice. Exiting.")
    sys.exit(1)

# =============================================================================
# STEP 3: CONFIRM AND START DOWNLOAD
# =============================================================================

print("\n" + "="*80)
print("DOWNLOAD SUMMARY")
print("="*80)

total_size_mb = len(downloads) * 250
total_time_min = len(downloads) * 10

print(f"\nNumber of downloads: {len(downloads)}")
print(f"Estimated total size: ~{total_size_mb} MB")
print(f"Estimated total time: ~{total_time_min} minutes")
print("\nDownloads:")
for version, year in downloads:
    gloria_folder = parent_dir / "GLORIA_db" / f"v{version}" / str(year) / "raw_download"
    print(f"  - Version {version}, Year {year}")
    print(f"    → {gloria_folder}")

print("\n⚠ Make sure you have:")
print("  - Stable internet connection")
print(f"  - At least {total_size_mb * 2} MB free disk space")
print("  - Time to wait for download completion")

confirm = input("\nProceed with download? (y/n): ").strip().lower()

if confirm != 'y':
    print("\nDownload cancelled. Exiting.")
    sys.exit(0)

# =============================================================================
# STEP 4: DOWNLOAD GLORIA DATA
# =============================================================================

print("\n" + "="*80)
print("DOWNLOADING GLORIA DATA")
print("="*80)

successful_downloads = []
failed_downloads = []

for idx, (version, year) in enumerate(downloads, 1):
    print(f"\n{'-'*80}")
    print(f"Download {idx}/{len(downloads)}: Version {version}, Year {year}")
    print(f"{'-'*80}")

    # Setup folder
    gloria_folder = parent_dir / "GLORIA_db" / f"v{version}" / str(year) / "raw_download"
    gloria_folder.mkdir(parents=True, exist_ok=True)

    print(f"Destination: {gloria_folder}")

    # Check if already exists
    existing_files = list(gloria_folder.glob("GLORIA_MRIOs_*.zip")) + \
                    list(gloria_folder.glob("download_log.json"))

    if existing_files:
        print(f"\n⚠ Found {len(existing_files)} existing file(s) in destination")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Skipping this download...")
            continue

    # Start download
    start_time = datetime.now()
    print(f"\nStarting download at {start_time.strftime('%H:%M:%S')}...")
    print("Please wait. This will take several minutes...")
    print("(You can monitor your internet connection to see download progress)")

    try:
        # Download using pymrio
        gloria_log = pymrio.download_gloria(
            storage_folder=str(gloria_folder),
            year=year,
            version=version
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✓ Download completed successfully!")
        print(f"   Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")

        # Show download log
        print(f"\nDownload log:")
        print(gloria_log)

        # Save download info
        info_file = gloria_folder / "download_info.txt"
        with open(info_file, 'w') as f:
            f.write(f"GLORIA Download Information\n")
            f.write(f"="*60 + "\n")
            f.write(f"Version: {version}\n")
            f.write(f"Year: {year}\n")
            f.write(f"Download date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration:.0f} seconds\n")
            f.write(f"Folder: {gloria_folder}\n")
            f.write(f"\n" + "="*60 + "\n")
            f.write(f"Download log:\n")
            f.write(str(gloria_log))

        print(f"\nDownload info saved to: {info_file}")

        # Check downloaded files
        downloaded_files = list(gloria_folder.glob("*"))
        print(f"\nFiles in download folder: {len(downloaded_files)}")
        for file in downloaded_files[:10]:  # Show first 10
            size_mb = file.stat().st_size / (1024**2) if file.is_file() else 0
            print(f"  - {file.name} ({size_mb:.1f} MB)")
        if len(downloaded_files) > 10:
            print(f"  ... and {len(downloaded_files) - 10} more files")

        successful_downloads.append((version, year, gloria_folder))

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✗ Download failed!")
        print(f"   Duration before failure: {duration:.0f} seconds")
        print(f"   Error: {str(e)}")

        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Verify you have enough disk space")
        print("  3. Try downloading manually from: https://www.gloria-mrio.com/")
        print("  4. Check if the version/year combination is available")

        failed_downloads.append((version, year, str(e)))

        if len(downloads) > 1:
            continue_download = input("\nContinue with remaining downloads? (y/n): ").strip().lower()
            if continue_download != 'y':
                print("Stopping downloads...")
                break

# =============================================================================
# STEP 5: DOWNLOAD SUMMARY
# =============================================================================

print("\n" + "="*80)
print("DOWNLOAD SUMMARY")
print("="*80)

if successful_downloads:
    print(f"\n✓ Successfully downloaded {len(successful_downloads)} dataset(s):")
    for version, year, folder in successful_downloads:
        print(f"   - Version {version}, Year {year}")
        print(f"     Location: {folder}")

        # Check file size
        total_size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
        print(f"     Size: {total_size / (1024**2):.1f} MB")

if failed_downloads:
    print(f"\n✗ Failed downloads: {len(failed_downloads)}")
    for version, year, error in failed_downloads:
        print(f"   - Version {version}, Year {year}")
        print(f"     Error: {error}")

# =============================================================================
# STEP 6: NEXT STEPS
# =============================================================================

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)

if successful_downloads:
    print("""
✓ GLORIA data downloaded successfully!

WHAT TO DO NEXT:

1. PARSE THE DATA (if needed)
   The downloaded data may need to be parsed into the format used by MINDSET.
   Check if you have these folders:

   GLORIA_db/v{version}/{year}/parsed_db/

   If not, you may need to run parsing scripts:
   - ParseCode/Parsing-Gloria-mat.py
   - ParseCode/Parsing-Gloria-pkl.py

2. RUN THE TUTORIAL
   Now you can run the Uganda employment impact tutorial with real data:

   python "Python Scripts - New/uganda_employment_impact_tutorial.py"

   When prompted, select option 1 to use the downloaded GLORIA data.

3. RUN MINDSET MODEL
   For full analysis with all MINDSET features:

   python RunMINDSET.py

   See README.md for detailed instructions.

4. VERIFY DATA
   You can verify the download by checking:
   - File sizes (should be ~200-300 MB per year)
   - Download log files
   - Ability to import with pymrio

   To test import:
   >>> import pymrio
   >>> gloria = pymrio.parse_gloria(path='{download_folder}')
   >>> print(gloria.get_regions())  # Should show list of countries

5. DOCUMENTATION
   For more information about GLORIA:
   - Website: https://www.gloria-mrio.com/
   - Documentation: https://www.gloria-mrio.com/docs
   - pymrio docs: https://pymrio.readthedocs.io/
    """.format(
        version=successful_downloads[0][0],
        year=successful_downloads[0][1],
        download_folder=successful_downloads[0][2].parent
    ))
else:
    print("""
✗ No successful downloads.

TROUBLESHOOTING:

1. Check internet connection
2. Verify pymrio installation: pip install pymrio
3. Try downloading manually from https://www.gloria-mrio.com/
4. Check available disk space
5. Try different version/year combination
6. Check firewall/proxy settings

For help, visit:
- pymrio documentation: https://pymrio.readthedocs.io/
- GLORIA website: https://www.gloria-mrio.com/
    """)

print("\n" + "="*80)
print("GLORIA DOWNLOADER - COMPLETE")
print("="*80)

# Create a download summary file
summary_file = parent_dir / "GLORIA_db" / "download_summary.txt"
summary_file.parent.mkdir(exist_ok=True)

with open(summary_file, 'a') as f:
    f.write(f"\n{'='*80}\n")
    f.write(f"Download Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"{'='*80}\n")

    if successful_downloads:
        f.write(f"\nSuccessful downloads: {len(successful_downloads)}\n")
        for version, year, folder in successful_downloads:
            f.write(f"  - Version {version}, Year {year}: {folder}\n")

    if failed_downloads:
        f.write(f"\nFailed downloads: {len(failed_downloads)}\n")
        for version, year, error in failed_downloads:
            f.write(f"  - Version {version}, Year {year}: {error}\n")

    f.write(f"\n")

print(f"\nDownload summary appended to: {summary_file}")
print("\nYou can now close this window or run another download.")
