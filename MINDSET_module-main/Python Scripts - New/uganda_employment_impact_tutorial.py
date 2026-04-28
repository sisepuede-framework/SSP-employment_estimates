"""
================================================================================
MINDSET MODEL - EMPLOYMENT IMPACT ANALYSIS FOR UGANDA
Comprehensive Tutorial with GLORIA Data Download
================================================================================

PURPOSE:
--------
This script demonstrates how to:
1. Download GLORIA MRIO data using pymrio
2. Load and prepare the data for Uganda
3. Run Input-Output (I-O) analysis
4. Estimate employment impacts from demand shocks

WHAT YOU'LL LEARN:
------------------
1. How to download GLORIA data automatically
2. How to work with Multi-Regional Input-Output (MRIO) data
3. The mathematics behind Leontief Input-Output models
4. How to calculate employment multipliers
5. How to interpret and visualize results

THEORETICAL BACKGROUND:
-----------------------
The Leontief Input-Output Model:
    x = (I - A)^(-1) * y = L * y

where:
    x = gross output vector (total production by each sector)
    A = technical coefficients matrix (input requirements per unit output)
    L = Leontief inverse = (I - A)^(-1) (total requirements matrix)
    y = final demand vector (consumption, investment, government, exports)

Employment Impacts:
    ΔE = e * L * Δy

where:
    ΔE = change in employment (jobs)
    e = employment coefficient (jobs per $ of output)
    L = Leontief inverse matrix
    Δy = change in final demand

Author: Tutorial Script
Date: March 2026
Version: 1.0
================================================================================
"""

# =============================================================================
# SECTION 1: IMPORT LIBRARIES AND CHECK DEPENDENCIES
# =============================================================================

print("="*80)
print("MINDSET EMPLOYMENT IMPACT ANALYSIS - UGANDA TUTORIAL")
print("="*80)
print("\n[Step 1/10] Checking dependencies...")

import sys
import os
from pathlib import Path

# First, check for pymrio (needed for GLORIA download)
try:
    import pymrio
    print(f"✓ pymrio installed (version {pymrio.__version__})")
    PYMRIO_AVAILABLE = True
except ImportError:
    print("✗ pymrio NOT installed")
    print("\n" + "="*80)
    print("PYMRIO INSTALLATION REQUIRED")
    print("="*80)
    print("""
pymrio is a Python library for Multi-Regional Input-Output analysis.
We'll use it to download GLORIA data automatically.

To install pymrio, run this command:
    pip install pymrio

After installation, re-run this script.
    """)
    install_now = input("Would you like to try installing it now? (y/n): ")

    if install_now.lower() == 'y':
        print("\nAttempting to install pymrio...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pymrio"])
            print("✓ pymrio installed successfully!")
            print("Please restart this script.")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Installation failed: {e}")
            print("Please install manually with: pip install pymrio")
            sys.exit(1)
    else:
        print("\nExiting. Please install pymrio and re-run this script.")
        sys.exit(1)

# Import other required libraries
try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle
    from datetime import datetime
    print("✓ All standard libraries available (numpy, pandas, matplotlib)")
except ImportError as e:
    print(f"✗ Missing required library: {e}")
    print("Please install with: pip install numpy pandas matplotlib")
    sys.exit(1)

# =============================================================================
# SECTION 2: GLORIA DATA DOWNLOAD SETUP
# =============================================================================

print("\n" + "="*80)
print("[Step 2/10] GLORIA DATA DOWNLOAD SETUP")
print("="*80)

print("""
GLORIA (Global Resource Input-Output Assessment) is a comprehensive
Multi-Regional Input-Output (MRIO) database covering:
    - 169 countries
    - 120 sectors per country
    - Years: 2000-2022
    - Version 57 (latest stable release)

We'll download data for 2019 (most recent pre-COVID year with complete data).
""")

# Set up paths
cwd = Path(os.getcwd())
gloria_base_folder = cwd / "GLORIA_db"
gloria_download_folder = gloria_base_folder / "v57" / "2019" / "raw_download"

print(f"\nGLORIA data will be stored in:")
print(f"  {gloria_download_folder}")

# Check if data already exists
data_exists = False
if gloria_download_folder.exists():
    # Check for key files
    potential_files = list(gloria_download_folder.glob("GLORIA_MRIOs_57_2019*"))
    if potential_files:
        print(f"\n✓ GLORIA data already downloaded ({len(potential_files)} files found)")
        data_exists = True

        user_choice = input("\nData already exists. Re-download? (y/n): ")
        if user_choice.lower() != 'y':
            print("Using existing data...")
        else:
            data_exists = False
            print("Will re-download data...")

if not data_exists:
    print("\n" + "-"*80)
    print("DOWNLOAD GLORIA DATA")
    print("-"*80)

    print("""
Download options:
1. Download year 2019, version 57 (Recommended for this tutorial)
2. Download different year/version
3. Skip download (use existing data or create synthetic example)
    """)

    download_choice = input("Enter choice (1-3): ")

    if download_choice == '1':
        # Download GLORIA 2019, version 57
        print("\nPreparing to download GLORIA 2019 (version 57)...")
        print("This will take 5-15 minutes depending on your internet connection...")
        print("File size: approximately 200-300 MB compressed")

        confirm = input("\nProceed with download? (y/n): ")

        if confirm.lower() == 'y':
            # Create download folder
            gloria_download_folder.mkdir(parents=True, exist_ok=True)

            print("\n" + "="*60)
            print("DOWNLOADING GLORIA DATA...")
            print("="*60)
            print("Please wait. This may take several minutes...")

            try:
                # Download GLORIA data using pymrio
                # This downloads the MRIO database for the specified year and version
                gloria_log = pymrio.download_gloria(
                    storage_folder=str(gloria_download_folder),
                    year=2019,
                    version=57
                )

                print("\n✓ Download complete!")
                print("\nDownload log:")
                print(gloria_log)

                # Save download log for reference
                log_file = gloria_download_folder / "download_info.txt"
                with open(log_file, 'w') as f:
                    f.write(str(gloria_log))
                print(f"\nDownload log saved to: {log_file}")

                data_exists = True

            except Exception as e:
                print(f"\n✗ Download failed: {e}")
                print("\nTroubleshooting:")
                print("1. Check your internet connection")
                print("2. Ensure you have enough disk space (~500 MB)")
                print("3. Try downloading manually from: https://www.gloria-mrio.com/")

                fallback = input("\nContinue with synthetic example instead? (y/n): ")
                if fallback.lower() == 'y':
                    data_exists = False
                else:
                    print("Exiting. Please resolve download issues and re-run.")
                    sys.exit(1)
        else:
            print("Download cancelled.")
            data_exists = False

    elif download_choice == '2':
        # Custom year/version
        print("\nAvailable GLORIA versions: 53-57 (57 is latest)")
        print("Available years: 2000-2022")

        year = input("Enter year (default=2019): ") or "2019"
        version = input("Enter version (default=57): ") or "57"

        gloria_download_folder = gloria_base_folder / f"v{version}" / year / "raw_download"
        gloria_download_folder.mkdir(parents=True, exist_ok=True)

        print(f"\nDownloading GLORIA {year} (version {version})...")

        try:
            gloria_log = pymrio.download_gloria(
                storage_folder=str(gloria_download_folder),
                year=int(year),
                version=int(version)
            )
            print("\n✓ Download complete!")
            print(gloria_log)
            data_exists = True

        except Exception as e:
            print(f"\n✗ Download failed: {e}")
            data_exists = False

    else:
        print("\nSkipping download. Will use synthetic example.")
        data_exists = False

# =============================================================================
# SECTION 3: LOAD GLORIA DATA OR CREATE SYNTHETIC EXAMPLE
# =============================================================================

print("\n" + "="*80)
print("[Step 3/10] DATA LOADING")
print("="*80)

if data_exists and PYMRIO_AVAILABLE:
    print("\nAttempting to load GLORIA data with pymrio...")

    try:
        # Parse GLORIA data using pymrio
        print("Parsing GLORIA database (this may take a few minutes)...")

        # Load the GLORIA data
        # pymrio automatically finds and loads the downloaded files
        gloria = pymrio.parse_gloria(path=str(gloria_download_folder.parent))

        print("✓ GLORIA data loaded successfully!")

        # Get basic information
        countries = gloria.get_regions()
        sectors = gloria.get_sectors()

        print(f"\nDatabase summary:")
        print(f"  Countries: {len(countries)}")
        print(f"  Sectors: {len(sectors)}")
        print(f"  Total dimensions: {len(countries)} × {len(sectors)} = {len(countries) * len(sectors)}")

        # Check for Uganda
        if 'UGA' in countries:
            print(f"\n✓ Uganda (UGA) found in database!")
            uganda_idx = countries.index('UGA')
            print(f"  Country index: {uganda_idx}")
            USE_REAL_DATA = True
        else:
            print("\n✗ Uganda not found in database")
            print(f"Available countries: {', '.join(countries[:20])}...")
            USE_REAL_DATA = False

    except Exception as e:
        print(f"\n✗ Error loading GLORIA data: {e}")
        print("Falling back to synthetic example...")
        USE_REAL_DATA = False
else:
    USE_REAL_DATA = False

# =============================================================================
# SECTION 4: CREATE SIMPLIFIED SYNTHETIC EXAMPLE
# =============================================================================

if not USE_REAL_DATA:
    print("\n" + "="*80)
    print("[Step 4/10] CREATING SYNTHETIC UGANDA ECONOMY")
    print("="*80)

    print("""
Since we don't have full GLORIA data loaded, we'll create a simplified
5-sector economy to demonstrate the methodology.

SECTORS:
1. Agriculture (AGR)      - Crops, livestock, fishing
2. Manufacturing (MAN)     - Processing, industrial production
3. Construction (CON)      - Buildings, infrastructure
4. Services (SER)          - Trade, transport, finance, education
5. Energy (ENE)            - Electricity, fuel production

This simplified model will teach you the exact same methodology used
in the full GLORIA analysis, just with fewer sectors.
    """)

    # Define sectors
    sectors = ['Agriculture', 'Manufacturing', 'Construction', 'Services', 'Energy']
    sector_codes = ['AGR', 'MAN', 'CON', 'SER', 'ENE']
    n_sectors = len(sectors)

    print(f"Economy structure: {n_sectors} sectors")

    # =========================================================================
    # Create Technical Coefficients Matrix (A)
    # =========================================================================
    print("\n" + "-"*80)
    print("Building Technical Coefficients Matrix (A)")
    print("-"*80)

    print("""
The A matrix represents the recipe for production in each sector.
Element A[i,j] = amount of input from sector i needed to produce
                 1 unit of output in sector j

Example: A[AGR, MAN] = 0.15 means Manufacturing needs $0.15 of
Agricultural products to produce $1 of Manufacturing output.

Key properties:
- Each column represents a sector's input requirements
- Column sums < 1 (can't need more than $1 input to make $1 output)
- Diagonal elements = within-sector usage
- Reflects technology and efficiency of production
    """)

    # Create realistic A matrix for Uganda
    # Based on typical developing economy structure:
    # - Agriculture is important input to many sectors
    # - Manufacturing and Construction are input-intensive
    # - Services less input-intensive
    # - Energy used by all sectors

    A = np.array([
        # Inputs needed per $1 output in:
        # AGR   MAN   CON   SER   ENE
        [0.10, 0.15, 0.05, 0.03, 0.02],  # from Agriculture
        [0.05, 0.20, 0.25, 0.05, 0.10],  # from Manufacturing
        [0.02, 0.08, 0.15, 0.03, 0.05],  # from Construction
        [0.08, 0.12, 0.10, 0.20, 0.08],  # from Services
        [0.03, 0.10, 0.05, 0.05, 0.25]   # from Energy
    ])

    # Display A matrix
    A_df = pd.DataFrame(A,
                        index=[f"{s} (input)" for s in sector_codes],
                        columns=[f"{s} (output)" for s in sector_codes])

    print("\nTechnical Coefficients Matrix (A):")
    print(A_df.round(3).to_string())

    # Analyze the matrix
    print("\n" + "-"*40)
    print("Matrix Analysis:")
    print("-"*40)

    # Column sums (total inputs needed)
    col_sums = A.sum(axis=0)
    print("\nTotal intermediate inputs per $1 output:")
    for i, (code, sum_val) in enumerate(zip(sector_codes, col_sums)):
        value_added = 1 - sum_val
        print(f"  {code}: ${sum_val:.3f} → Value added = ${value_added:.3f}")

    # Row sums (how much each sector supplies to others)
    row_sums = A.sum(axis=1)
    print("\nTotal supply to other sectors (per column $1):")
    for i, (code, sum_val) in enumerate(zip(sector_codes, row_sums)):
        print(f"  {code}: ${sum_val:.3f}")

    # =========================================================================
    # Calculate Leontief Inverse (L)
    # =========================================================================
    print("\n" + "-"*80)
    print("Calculating Leontief Inverse Matrix (L)")
    print("-"*80)

    print("""
The Leontief inverse L = (I - A)^(-1) is the CORE of I-O analysis.

Mathematical derivation:
    x = Ax + y           (output = intermediate use + final demand)
    x - Ax = y           (rearrange)
    (I - A)x = y         (factor out x)
    x = (I - A)^(-1 * y   (solve for x)
    x = L * y            (define L = Leontief inverse)

Interpretation of L[i,j]:
- If final demand for sector j increases by $1
- Then sector i must produce $L[i,j] of total output
- This includes:
  • Direct requirements (from A matrix)
  • Indirect requirements (through supply chains)
  • All higher-order effects

Properties:
- Diagonal elements always ≥ 1 (at minimum, sector produces for itself)
- Off-diagonal elements show inter-sector linkages
- Larger elements = stronger multiplier effects
    """)

    # Calculate Leontief inverse
    I = np.eye(n_sectors)  # Identity matrix
    try:
        L = np.linalg.inv(I - A)
        print("✓ Leontief inverse calculated successfully")
    except np.linalg.LinAlgError:
        print("✗ Error: (I-A) matrix is singular (cannot invert)")
        print("This means the A matrix is economically infeasible.")
        sys.exit(1)

    # Display L matrix
    L_df = pd.DataFrame(L,
                        index=[f"{s} (output)" for s in sector_codes],
                        columns=[f"{s} (demand)" for s in sector_codes])

    print("\nLeontief Inverse Matrix (L):")
    print(L_df.round(3).to_string())

    # Analyze multipliers
    print("\n" + "-"*40)
    print("Sector Output Multipliers:")
    print("-"*40)
    print("(How much total output is generated per $1 of final demand)\n")

    for i, (sector, code) in enumerate(zip(sectors, sector_codes)):
        total_multiplier = L[:, i].sum()
        direct_effect = L[i, i]
        indirect_effect = total_multiplier - direct_effect

        print(f"{code} - {sector}:")
        print(f"  Total multiplier:    ${total_multiplier:.3f}")
        print(f"  Direct effect:       ${direct_effect:.3f} ({direct_effect/total_multiplier*100:.1f}%)")
        print(f"  Indirect effects:    ${indirect_effect:.3f} ({indirect_effect/total_multiplier*100:.1f}%)")
        print()

    # =========================================================================
    # Create Baseline Final Demand (y)
    # =========================================================================
    print("-"*80)
    print("Defining Baseline Final Demand (y)")
    print("-"*80)

    print("""
Final demand represents purchases by:
1. Households (consumption of goods/services)
2. Government (public sector spending)
3. Firms (investment in capital equipment)
4. Foreign buyers (exports)

This is DISTINCT from intermediate demand (sectors buying inputs
from each other, captured in the A matrix).

We'll create realistic final demand values for Uganda based on:
- GDP composition
- Economic structure (agriculture-dominant economy)
- Development level (lower-middle income country)

Values in millions of USD (2019 prices)
    """)

    # Create baseline final demand
    # Based on Uganda's economic structure (~$35 billion GDP in 2019)
    # Agriculture ~24%, Services ~43%, Industry ~26%, with remaining ~7%

    y_baseline = np.array([
        3500,   # Agriculture (large sector, but lower value-added)
        2000,   # Manufacturing (growing but still developing)
        1200,   # Construction (infrastructure investment)
        4000,   # Services (largest sector by value)
        800     # Energy (smaller but essential)
    ])

    # Display final demand
    demand_df = pd.DataFrame({
        'Sector': sectors,
        'Code': sector_codes,
        'Final Demand ($M)': y_baseline,
        'Share (%)': (y_baseline / y_baseline.sum() * 100).round(1)
    })

    print("\nBaseline Final Demand:")
    print(demand_df.to_string(index=False))
    print(f"\nTotal Final Demand: ${y_baseline.sum():,.0f} million")
    print(f"(Approximates Uganda's GDP structure)")

    # =========================================================================
    # Calculate Baseline Gross Output (x)
    # =========================================================================
    print("\n" + "-"*80)
    print("Calculating Baseline Gross Output (x = L · y)")
    print("-"*80)

    print("""
Gross output is TOTAL production by each sector, including:
- Output sold to final demand (y)
- Output used as intermediate inputs by other sectors (Ax)

The fundamental I-O identity:
    x = Ax + y    (output = intermediate use + final use)

Solving this using the Leontief inverse:
    x = L · y = (I - A)^(-1) · y

Key relationship:
    Value Added = x - Ax    (gross output minus intermediate inputs)

For the whole economy:
    GDP ≈ Sum of Value Added across all sectors
    """)

    # Calculate baseline gross output
    x_baseline = L @ y_baseline  # Matrix multiplication

    # Calculate value added
    intermediate_use = A @ x_baseline
    value_added_by_sector = x_baseline - intermediate_use
    total_gdp = value_added_by_sector.sum()

    # Display results
    output_df = pd.DataFrame({
        'Sector': sectors,
        'Code': sector_codes,
        'Final Demand (y)': y_baseline,
        'Gross Output (x)': x_baseline.round(0),
        'Multiplier (x/y)': (x_baseline / y_baseline).round(2),
        'Value Added ($M)': value_added_by_sector.round(0),
        'VA %': (value_added_by_sector / total_gdp * 100).round(1)
    })

    print("\nBaseline Economic Structure:")
    print(output_df.to_string(index=False))

    print(f"\n{'='*60}")
    print(f"Total Final Demand: ${y_baseline.sum():,.0f}M")
    print(f"Total Gross Output: ${x_baseline.sum():,.0f}M")
    print(f"Total GDP (Value Added): ${total_gdp:,.0f}M")
    print(f"{'='*60}")

    print("\nNote: Gross Output > GDP because it includes intermediate transactions")
    print(f"Ratio of Output to GDP: {x_baseline.sum() / total_gdp:.2f}")

    # =========================================================================
    # Create Employment Coefficients (e)
    # =========================================================================
    print("\n" + "-"*80)
    print("Defining Employment Coefficients (e)")
    print("-"*80)

    print("""
Employment coefficients measure labor intensity:
    e[i] = employment in sector i / output of sector i

Units: workers per million USD of output

These coefficients vary widely by:
1. Technology (labor vs. capital intensive)
2. Development level (developing countries more labor-intensive)
3. Sector characteristics
   - Agriculture: Very labor-intensive (manual work)
   - Manufacturing: Capital-intensive (machinery)
   - Construction: Labor-intensive (many workers)
   - Services: Labor-intensive (people-oriented)
   - Energy: Capital-intensive (automated plants)

Formula for employment:
    Employment = e · x

where:
    e = employment coefficient (workers/$M output)
    x = gross output ($M)
    """)

    # Create employment coefficients
    # Based on typical labor intensities in Sub-Saharan Africa
    employment_coef = np.array([
        280,   # Agriculture (very labor-intensive, small-scale farms)
        95,    # Manufacturing (some capital equipment)
        150,   # Construction (labor-intensive, manual work)
        220,   # Services (high employment, lower productivity)
        50     # Energy (capital-intensive, few workers)
    ])

    # Calculate baseline employment
    employment_baseline = employment_coef * x_baseline
    total_employment = employment_baseline.sum()

    # Calculate productivity
    productivity = x_baseline / employment_baseline * 1000  # Output per worker ($1000s)

    # Display employment data
    empl_df = pd.DataFrame({
        'Sector': sectors,
        'Code': sector_codes,
        'Coef (jobs/$M)': employment_coef,
        'Output ($M)': x_baseline.round(0),
        'Employment': employment_baseline.round(0),
        'Share (%)': (employment_baseline / total_employment * 100).round(1),
        'Productivity ($K/worker)': productivity.round(1)
    })

    print("\nEmployment Structure:")
    print(empl_df.to_string(index=False))

    print(f"\n{'='*60}")
    print(f"Total Employment: {total_employment:,.0f} workers")
    print(f"Average Productivity: ${(x_baseline.sum() / total_employment * 1000):,.0f}/worker")
    print(f"GDP per worker: ${(total_gdp / total_employment * 1000):,.0f}/worker")
    print(f"{'='*60}")

    # Store all synthetic data
    synthetic_data = {
        'sectors': sectors,
        'sector_codes': sector_codes,
        'n_sectors': n_sectors,
        'A': A,
        'L': L,
        'y_baseline': y_baseline,
        'x_baseline': x_baseline,
        'employment_coef': employment_coef,
        'employment_baseline': employment_baseline,
        'value_added': value_added_by_sector,
        'gdp': total_gdp
    }

    print("\n✓ Synthetic Uganda economy created successfully!")

# =============================================================================
# SECTION 5: DEFINE DEMAND SHOCK SCENARIO
# =============================================================================

print("\n" + "="*80)
print("[Step 5/10] DEFINING DEMAND SHOCK SCENARIO")
print("="*80)

if not USE_REAL_DATA:
    print("""
POLICY SCENARIO: Infrastructure Investment Program
---------------------------------------------------
The Government of Uganda announces a major infrastructure investment:
- New roads connecting rural areas to markets
- Bridge construction over major rivers
- School and hospital buildings
- Water and sanitation infrastructure

This creates a POSITIVE DEMAND SHOCK to the Construction sector.

RESEARCH QUESTIONS:
1. How does this investment affect output across ALL sectors?
2. How many jobs are created in Construction (direct effect)?
3. How many jobs are created in other sectors (indirect effects)?
4. What is the total economic multiplier?
5. What is the cost per job created?
    """)

    # Get investment amount from user
    print("-"*80)
    default_investment = 800  # million USD
    user_input = input(f"Enter infrastructure investment ($M) [default={default_investment}]: ")

    try:
        investment_amount = float(user_input) if user_input.strip() else default_investment
    except ValueError:
        print(f"Invalid input. Using default: ${default_investment}M")
        investment_amount = default_investment

    print(f"\n✓ Simulating ${investment_amount:,.0f} million investment in Construction")

    # =========================================================================
    # Create Shock Vector (Δy)
    # =========================================================================
    print("\n" + "-"*80)
    print("Creating Demand Shock Vector (Δy)")
    print("-"*80)

    print("""
The shock vector represents the change in final demand.

For our infrastructure investment:
- ΔyConstruction = +$800M (new government spending)
- ΔyOther sectors = $0 (no direct change)

Note: This is the PRIMARY shock. Secondary effects (like increased
household consumption from new wages) would require a more complex
model with income-expenditure feedback loops.
    """)

    # Create shock vector
    delta_y = np.zeros(n_sectors)
    delta_y[2] = investment_amount  # Index 2 = Construction

    # Display shock
    shock_df = pd.DataFrame({
        'Sector': sectors,
        'Code': sector_codes,
        'Δ Final Demand ($M)': delta_y
    })

    print("\nDemand Shock (Δy):")
    print(shock_df.to_string(index=False))

# =============================================================================
# SECTION 6: CALCULATE OUTPUT IMPACTS
# =============================================================================

print("\n" + "="*80)
print("[Step 6/10] CALCULATING OUTPUT IMPACTS")
print("="*80)

if not USE_REAL_DATA:
    print("""
OUTPUT IMPACT CALCULATION
-------------------------
We use the Leontief model to calculate how the demand shock
propagates through the economy:

    Δx = L · Δy

This equation captures THREE types of effects:

1. DIRECT EFFECT:
   - Construction sector must produce more to meet new demand
   - Δx[Construction] includes the $800M investment itself

2. INDIRECT EFFECTS:
   - Construction needs inputs from other sectors
   - Those sectors need inputs from yet other sectors
   - Creates a ripple effect through supply chains

3. The Leontief inverse (L) automatically accounts for
   ALL rounds of these effects through matrix inversion

Let's calculate and analyze each component...
    """)

    # Calculate output impact
    print("Computing: Δx = L · Δy")
    delta_x = L @ delta_y
    x_new = x_baseline + delta_x

    # Calculate percentage changes
    pct_change_x = (delta_x / x_baseline) * 100

    # Decompose effects
    direct_output = delta_x[2]  # Construction sector
    indirect_output = delta_x.sum() - direct_output
    total_multiplier = delta_x.sum() / investment_amount

    print("\n" + "="*60)
    print("OUTPUT IMPACT RESULTS")
    print("="*60)

    # Display detailed results
    impact_df = pd.DataFrame({
        'Sector': sectors,
        'Code': sector_codes,
        'Baseline ($M)': x_baseline.round(0),
        'Δ Output ($M)': delta_x.round(1),
        '% Change': pct_change_x.round(2),
        'New Output ($M)': x_new.round(0)
    })

    print("\nSectoral Output Impacts:")
    print(impact_df.to_string(index=False))

    print(f"\n{'-'*60}")
    print("SUMMARY STATISTICS:")
    print(f"{'-'*60}")
    print(f"Investment in Construction:     ${investment_amount:,.1f}M")
    print(f"Total Output Generated:         ${delta_x.sum():,.1f}M")
    print(f"Output Multiplier:              {total_multiplier:.3f}")
    print(f"\n  → Every $1 invested generates ${total_multiplier:.2f} of total output")

    print(f"\n{'-'*60}")
    print("MULTIPLIER DECOMPOSITION:")
    print(f"{'-'*60}")
    print(f"Direct Effect (Construction):   ${direct_output:,.1f}M  ({direct_output/delta_x.sum()*100:.1f}%)")
    print(f"Indirect Effects (Other):       ${indirect_output:,.1f}M  ({indirect_output/delta_x.sum()*100:.1f}%)")

    # Analyze supply chain effects
    print(f"\n{'-'*60}")
    print("TOP SUPPLY CHAIN EFFECTS:")
    print(f"{'-'*60}")

    # Create sorted list of indirect impacts
    indirect_impacts = [(i, sectors[i], sector_codes[i], delta_x[i])
                        for i in range(n_sectors) if i != 2]
    indirect_impacts.sort(key=lambda x: x[3], reverse=True)

    print("\nSectors benefiting from supplying to Construction:\n")
    for rank, (idx, sector, code, impact) in enumerate(indirect_impacts, 1):
        pct_of_total = impact / delta_x.sum() * 100
        pct_of_baseline = impact / x_baseline[idx] * 100
        print(f"{rank}. {code} - {sector:15s}: ${impact:8.1f}M  "
              f"({pct_of_total:5.1f}% of total impact, "
              f"+{pct_of_baseline:5.2f}% vs baseline)")

    # Explain the supply chains
    print(f"\n{'-'*60}")
    print("SUPPLY CHAIN INTERPRETATION:")
    print(f"{'-'*60}")
    print("""
The indirect effects show how Construction investment ripples through
the economy:

1. Manufacturing (+$""" + f"{delta_x[1]:.1f}M):" + """
   - Construction buys cement, steel, equipment
   - Manufacturing must increase production to supply these

2. Energy (+$""" + f"{delta_x[4]:.1f}M):" + """
   - Construction sites need electricity, fuel
   - Manufacturing also needs energy for production
   - Creates compounded energy demand

3. Services (+$""" + f"{delta_x[3]:.1f}M):" + """
   - Transport services to move materials
   - Engineering/design services
   - Financial services for payments

4. Agriculture (+$""" + f"{delta_x[0]:.1f}M):" + """
   - Food for construction workers
   - Raw materials (timber, etc.)
   - Inputs to manufacturing (for workers there too)

This is the power of I-O analysis: it traces all these linkages
automatically through the Leontief inverse matrix!
    """)

# =============================================================================
# SECTION 7: CALCULATE EMPLOYMENT IMPACTS
# =============================================================================

print("\n" + "="*80)
print("[Step 7/10] CALCULATING EMPLOYMENT IMPACTS")
print("="*80)

if not USE_REAL_DATA:
    print("""
EMPLOYMENT IMPACT CALCULATION
------------------------------
We calculate employment changes using:

    ΔE = e · Δx

where:
    ΔE[i] = change in employment in sector i (number of workers)
    e[i] = employment coefficient for sector i (workers per $M output)
    Δx[i] = change in output in sector i ($M)

This is a simple linear relationship, assuming:
- Employment scales proportionally with output
- No technology changes in short run
- No labor supply constraints

These are reasonable assumptions for:
- Short-term analysis (1-2 years)
- Moderate-sized shocks
- Economies with labor surplus (like Uganda)
    """)

    # Calculate employment impacts
    print("Computing: ΔE = e · Δx")
    delta_employment = employment_coef * delta_x
    employment_new = employment_baseline + delta_employment
    pct_change_employment = (delta_employment / employment_baseline) * 100

    # Decompose employment effects
    direct_jobs = delta_employment[2]  # Construction
    indirect_jobs = delta_employment.sum() - direct_jobs
    employment_multiplier = delta_employment.sum() / investment_amount
    cost_per_job = (investment_amount * 1e6) / delta_employment.sum()  # Convert to $ per job

    print("\n" + "="*60)
    print("EMPLOYMENT IMPACT RESULTS")
    print("="*60)

    # Display detailed results
    empl_impact_df = pd.DataFrame({
        'Sector': sectors,
        'Code': sector_codes,
        'Baseline Jobs': employment_baseline.round(0),
        'Δ Employment': delta_employment.round(0),
        '% Change': pct_change_employment.round(2),
        'New Employment': employment_new.round(0),
        'Share of New Jobs': (delta_employment / delta_employment.sum() * 100).round(1)
    })

    print("\nSectoral Employment Impacts:")
    print(empl_impact_df.to_string(index=False))

    print(f"\n{'-'*60}")
    print("SUMMARY STATISTICS:")
    print(f"{'-'*60}")
    print(f"Investment Amount:              ${investment_amount:,.1f}M")
    print(f"Total Jobs Created:             {delta_employment.sum():,.0f} workers")
    print(f"Employment Multiplier:          {employment_multiplier:.1f} jobs per $M")
    print(f"Cost per Job:                   ${cost_per_job:,.0f}")
    print(f"\n  → Every $1M invested creates {employment_multiplier:.0f} jobs")
    print(f"  → Creating one job costs ${cost_per_job:,.0f}")

    print(f"\n{'-'*60}")
    print("EMPLOYMENT DECOMPOSITION:")
    print(f"{'-'*60}")
    print(f"Direct Jobs (Construction):     {direct_jobs:,.0f}  ({direct_jobs/delta_employment.sum()*100:.1f}%)")
    print(f"Indirect Jobs (Other Sectors):  {indirect_jobs:,.0f}  ({indirect_jobs/delta_employment.sum()*100:.1f}%)")

    # Analyze employment by sector
    print(f"\n{'-'*60}")
    print("EMPLOYMENT CREATION BY SECTOR:")
    print(f"{'-'*60}")

    empl_by_sector = [(i, sectors[i], sector_codes[i], delta_employment[i])
                      for i in range(n_sectors)]
    empl_by_sector.sort(key=lambda x: x[3], reverse=True)

    print("\nRanking of job creation:\n")
    for rank, (idx, sector, code, jobs) in enumerate(empl_by_sector, 1):
        pct_of_total = jobs / delta_employment.sum() * 100
        pct_of_baseline = jobs / employment_baseline[idx] * 100
        print(f"{rank}. {code} - {sector:15s}: {jobs:8,.0f} jobs  "
              f"({pct_of_total:5.1f}% of new jobs, "
              f"+{pct_of_baseline:5.2f}% vs baseline)")

    # Explain employment patterns
    print(f"\n{'-'*60}")
    print("EMPLOYMENT PATTERN INTERPRETATION:")
    print(f"{'-'*60}")
    print(f"""
Key insights from employment impacts:

1. CONSTRUCTION DOMINATES ({direct_jobs:,.0f} jobs, {direct_jobs/delta_employment.sum()*100:.1f}%):
   - High labor intensity (coef = {employment_coef[2]} workers/$M)
   - Direct recipient of investment
   - Typical for infrastructure programs

2. AGRICULTURE SIGNIFICANT ({delta_employment[0]:,.0f} jobs, {delta_employment[0]/delta_employment.sum()*100:.1f}%):
   - Very high labor intensity (coef = {employment_coef[0]} workers/$M)
   - Even small output increases create many jobs
   - Important for poverty reduction (agricultural jobs)

3. SERVICES SUBSTANTIAL ({delta_employment[3]:,.0f} jobs, {delta_employment[3]/delta_employment.sum()*100:.1f}%):
   - Moderate labor intensity
   - Support services for construction and other sectors
   - Often overlooked but important

4. ENERGY MODEST ({delta_employment[4]:,.0f} jobs, {delta_employment[4]/delta_employment.sum()*100:.1f}%):
   - Low labor intensity (capital-intensive sector)
   - High output increase doesn't translate to many jobs
   - But essential for overall production

POLICY RELEVANCE:
- For every 1 direct job in Construction, {indirect_jobs/direct_jobs:.2f} indirect jobs created
- Stronger case for infrastructure investment (employment > just construction)
- Agriculture and services benefit significantly (poverty impact)
- Total multiplier effect justifies public investment
    """)

# =============================================================================
# SECTION 8: VISUALIZE RESULTS
# =============================================================================

print("\n" + "="*80)
print("[Step 8/10] VISUALIZING RESULTS")
print("="*80)

if not USE_REAL_DATA:
    print("Creating comprehensive visualization of impacts...\n")

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # Main title
    fig.suptitle(f'Uganda Infrastructure Investment Impact Analysis\n'
                 f'${investment_amount:,.0f}M Construction Investment - Employment & Output Effects',
                 fontsize=16, fontweight='bold', y=0.98)

    # Color scheme
    color_construction = '#2ecc71'  # Green
    color_other = '#3498db'         # Blue
    color_output = '#e74c3c'        # Red
    color_employment = '#f39c12'    # Orange

    # -------------------------------------------------------------------------
    # Plot 1: Output Impact by Sector (bar chart)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    colors1 = [color_construction if i == 2 else color_other for i in range(n_sectors)]
    bars1 = ax1.bar(range(n_sectors), delta_x, color=colors1, alpha=0.7, edgecolor='black')

    ax1.set_xticks(range(n_sectors))
    ax1.set_xticklabels(sector_codes, fontweight='bold')
    ax1.set_ylabel('Output Change (million USD)', fontsize=10, fontweight='bold')
    ax1.set_title('Output Impact by Sector', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_axisbelow(True)

    # Add value labels
    for bar, val in zip(bars1, delta_x):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${val:.0f}M', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # -------------------------------------------------------------------------
    # Plot 2: Employment Impact by Sector (bar chart)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    colors2 = [color_construction if i == 2 else color_employment for i in range(n_sectors)]
    bars2 = ax2.bar(range(n_sectors), delta_employment, color=colors2, alpha=0.7, edgecolor='black')

    ax2.set_xticks(range(n_sectors))
    ax2.set_xticklabels(sector_codes, fontweight='bold')
    ax2.set_ylabel('Employment Change (workers)', fontsize=10, fontweight='bold')
    ax2.set_title('Employment Impact by Sector', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_axisbelow(True)

    # Add value labels
    for bar, val in zip(bars2, delta_employment):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # -------------------------------------------------------------------------
    # Plot 3: Direct vs Indirect Effects (grouped bar)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[0, 2])

    x_pos = np.arange(2)
    width = 0.35

    direct_values = [direct_output, direct_jobs]
    indirect_values = [indirect_output, indirect_jobs]

    bars3a = ax3.bar(x_pos - width/2, direct_values, width,
                     label='Direct', color=color_construction, alpha=0.7, edgecolor='black')
    bars3b = ax3.bar(x_pos + width/2, indirect_values, width,
                     label='Indirect', color=color_other, alpha=0.7, edgecolor='black')

    ax3.set_ylabel('Impact (Output: $M, Employment: jobs)', fontsize=9, fontweight='bold')
    ax3.set_title('Direct vs Indirect Effects', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(['Output\n($M)', 'Employment\n(jobs)'], fontweight='bold')
    ax3.legend(loc='upper right', framealpha=0.9)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    ax3.set_axisbelow(True)

    # Add value labels
    for bars in [bars3a, bars3b]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=8)

    # -------------------------------------------------------------------------
    # Plot 4: Output Multiplier Breakdown (pie chart)
    # -------------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 0])

    output_shares = delta_x / delta_x.sum() * 100
    colors_pie1 = [color_construction if i == 2 else plt.cm.Blues(0.3 + i*0.15)
                   for i in range(n_sectors)]

    wedges, texts, autotexts = ax4.pie(delta_x, labels=sector_codes, autopct='%1.1f%%',
                                        colors=colors_pie1, startangle=90,
                                        wedgeprops=dict(edgecolor='black', linewidth=1.5))

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    ax4.set_title(f'Output Impact Distribution\nTotal: ${delta_x.sum():.0f}M',
                  fontsize=12, fontweight='bold')

    # -------------------------------------------------------------------------
    # Plot 5: Employment Creation Breakdown (pie chart)
    # -------------------------------------------------------------------------
    ax5 = fig.add_subplot(gs[1, 1])

    colors_pie2 = [color_construction if i == 2 else plt.cm.Oranges(0.3 + i*0.15)
                   for i in range(n_sectors)]

    wedges, texts, autotexts = ax5.pie(delta_employment, labels=sector_codes, autopct='%1.1f%%',
                                        colors=colors_pie2, startangle=90,
                                        wedgeprops=dict(edgecolor='black', linewidth=1.5))

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    ax5.set_title(f'Employment Creation Distribution\nTotal: {delta_employment.sum():,.0f} jobs',
                  fontsize=12, fontweight='bold')

    # -------------------------------------------------------------------------
    # Plot 6: Economic Multipliers (bar chart)
    # -------------------------------------------------------------------------
    ax6 = fig.add_subplot(gs[1, 2])

    multipliers = [total_multiplier, employment_multiplier]
    multiplier_labels = ['Output\nMultiplier', 'Employment\nMultiplier\n(jobs/$M)']
    colors_mult = [color_output, color_employment]

    bars6 = ax6.bar(range(2), multipliers, color=colors_mult, alpha=0.7,
                    edgecolor='black', linewidth=1.5)

    ax6.set_xticks(range(2))
    ax6.set_xticklabels(multiplier_labels, fontweight='bold')
    ax6.set_ylabel('Multiplier Value', fontsize=10, fontweight='bold')
    ax6.set_title('Economic Multipliers', fontsize=12, fontweight='bold')
    ax6.grid(axis='y', alpha=0.3, linestyle='--')
    ax6.set_axisbelow(True)

    # Add value labels
    for bar, val, label in zip(bars6, multipliers, multiplier_labels):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # -------------------------------------------------------------------------
    # Plot 7: Output Changes (horizontal bar - sorted)
    # -------------------------------------------------------------------------
    ax7 = fig.add_subplot(gs[2, 0])

    # Sort by output change
    sorted_indices = np.argsort(delta_x)
    sorted_codes = [sector_codes[i] for i in sorted_indices]
    sorted_output = delta_x[sorted_indices]
    sorted_colors = [color_construction if i == 2 else color_other for i in sorted_indices]

    bars7 = ax7.barh(range(n_sectors), sorted_output, color=sorted_colors,
                     alpha=0.7, edgecolor='black')

    ax7.set_yticks(range(n_sectors))
    ax7.set_yticklabels(sorted_codes, fontweight='bold')
    ax7.set_xlabel('Output Change ($M)', fontsize=10, fontweight='bold')
    ax7.set_title('Output Ranking', fontsize=12, fontweight='bold')
    ax7.grid(axis='x', alpha=0.3, linestyle='--')
    ax7.set_axisbelow(True)

    # Add value labels
    for bar, val in zip(bars7, sorted_output):
        width = bar.get_width()
        ax7.text(width, bar.get_y() + bar.get_height()/2.,
                f' ${val:.0f}M', ha='left', va='center', fontsize=8)

    # -------------------------------------------------------------------------
    # Plot 8: Employment Changes (horizontal bar - sorted)
    # -------------------------------------------------------------------------
    ax8 = fig.add_subplot(gs[2, 1])

    # Sort by employment change
    sorted_indices_e = np.argsort(delta_employment)
    sorted_codes_e = [sector_codes[i] for i in sorted_indices_e]
    sorted_employment = delta_employment[sorted_indices_e]
    sorted_colors_e = [color_construction if i == 2 else color_employment for i in sorted_indices_e]

    bars8 = ax8.barh(range(n_sectors), sorted_employment, color=sorted_colors_e,
                     alpha=0.7, edgecolor='black')

    ax8.set_yticks(range(n_sectors))
    ax8.set_yticklabels(sorted_codes_e, fontweight='bold')
    ax8.set_xlabel('Employment Change (jobs)', fontsize=10, fontweight='bold')
    ax8.set_title('Employment Ranking', fontsize=12, fontweight='bold')
    ax8.grid(axis='x', alpha=0.3, linestyle='--')
    ax8.set_axisbelow(True)

    # Add value labels
    for bar, val in zip(bars8, sorted_employment):
        width = bar.get_width()
        ax8.text(width, bar.get_y() + bar.get_height()/2.,
                f' {val:.0f}', ha='left', va='center', fontsize=8)

    # -------------------------------------------------------------------------
    # Plot 9: Key Metrics Summary (text box)
    # -------------------------------------------------------------------------
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')

    summary_text = f"""
KEY IMPACT METRICS

Investment
• Amount: ${investment_amount:,.0f}M
• Sector: Construction

Output Effects
• Total Output: ${delta_x.sum():,.0f}M
• Multiplier: {total_multiplier:.2f}
• Direct: ${direct_output:,.0f}M ({direct_output/delta_x.sum()*100:.0f}%)
• Indirect: ${indirect_output:,.0f}M ({indirect_output/delta_x.sum()*100:.0f}%)

Employment Effects
• Total Jobs: {delta_employment.sum():,.0f}
• Multiplier: {employment_multiplier:.1f} jobs/$M
• Direct: {direct_jobs:,.0f} ({direct_jobs/delta_employment.sum()*100:.0f}%)
• Indirect: {indirect_jobs:,.0f} ({indirect_jobs/delta_employment.sum()*100:.0f}%)

Cost Efficiency
• Cost/Job: ${cost_per_job:,.0f}
• Output/Job: ${delta_x.sum()/delta_employment.sum():.2f}M

Interpretation
Every $1M invested creates:
→ ${total_multiplier:.2f}M total output
→ {employment_multiplier:.0f} total jobs
    """

    ax9.text(0.1, 0.95, summary_text, transform=ax9.transAxes,
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Save figure
    output_dir = Path(cwd) / "GLORIA_results"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    figure_path = output_dir / f"uganda_employment_impact_{timestamp}.png"

    plt.savefig(figure_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Visualization saved: {figure_path}")

    # Show the plot
    plt.show()
    print("\n(Close the figure window to continue...)")

# =============================================================================
# SECTION 9: EXPORT RESULTS
# =============================================================================

print("\n" + "="*80)
print("[Step 9/10] EXPORTING RESULTS")
print("="*80)

if not USE_REAL_DATA:
    print("Exporting results to multiple formats...\n")

    # Create comprehensive results DataFrame
    results_main = pd.DataFrame({
        'Sector': sectors,
        'Sector_Code': sector_codes,
        # Baseline
        'Baseline_Final_Demand_M$': y_baseline,
        'Baseline_Gross_Output_M$': x_baseline.round(2),
        'Baseline_Employment': employment_baseline.round(0),
        'Baseline_Value_Added_M$': value_added_by_sector.round(2),
        # Shock
        'Demand_Shock_M$': delta_y,
        # Output impacts
        'Output_Change_M$': delta_x.round(2),
        'Output_Change_Pct': pct_change_x.round(3),
        'New_Gross_Output_M$': x_new.round(2),
        # Employment impacts
        'Employment_Change': delta_employment.round(0),
        'Employment_Change_Pct': pct_change_employment.round(3),
        'New_Employment': employment_new.round(0),
        # Coefficients
        'Employment_Coefficient': employment_coef
    })

    # Create summary statistics
    summary_stats = pd.DataFrame({
        'Metric': [
            'INVESTMENT',
            'Investment Amount ($M)',
            'Investment Sector',
            '',
            'OUTPUT IMPACTS',
            'Total Output Change ($M)',
            'Output Multiplier',
            'Direct Output Effect ($M)',
            'Indirect Output Effect ($M)',
            'Direct Effect Share (%)',
            'Indirect Effect Share (%)',
            '',
            'EMPLOYMENT IMPACTS',
            'Total Employment Change (jobs)',
            'Employment Multiplier (jobs/$M)',
            'Direct Employment Effect (jobs)',
            'Indirect Employment Effect (jobs)',
            'Direct Jobs Share (%)',
            'Indirect Jobs Share (%)',
            '',
            'COST EFFICIENCY',
            'Cost per Job Created ($)',
            'Output per New Job ($M)',
            'Jobs per $1M Invested',
            '',
            'BASELINE ECONOMY',
            'Total GDP (Value Added) ($M)',
            'Total Gross Output ($M)',
            'Total Employment (workers)',
            'GDP per Worker ($K)',
            'Output per Worker ($K)'
        ],
        'Value': [
            '',
            investment_amount,
            'Construction',
            '',
            '',
            delta_x.sum(),
            total_multiplier,
            direct_output,
            indirect_output,
            direct_output/delta_x.sum()*100,
            indirect_output/delta_x.sum()*100,
            '',
            '',
            delta_employment.sum(),
            employment_multiplier,
            direct_jobs,
            indirect_jobs,
            direct_jobs/delta_employment.sum()*100,
            indirect_jobs/delta_employment.sum()*100,
            '',
            '',
            cost_per_job,
            delta_x.sum()/delta_employment.sum(),
            employment_multiplier,
            '',
            '',
            total_gdp,
            x_baseline.sum(),
            employment_baseline.sum(),
            total_gdp/employment_baseline.sum()*1000,
            x_baseline.sum()/employment_baseline.sum()*1000
        ]
    })

    # Export to Excel with multiple sheets
    excel_path = output_dir / f"uganda_results_{timestamp}.xlsx"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Main results
        results_main.to_excel(writer, sheet_name='Sectoral_Results', index=False)

        # Summary statistics
        summary_stats.to_excel(writer, sheet_name='Summary_Statistics', index=False)

        # Technical matrices
        tech_coef_df = pd.DataFrame(A, index=sector_codes, columns=sector_codes)
        tech_coef_df.to_excel(writer, sheet_name='Tech_Coefficients_A')

        leontief_df = pd.DataFrame(L, index=sector_codes, columns=sector_codes)
        leontief_df.to_excel(writer, sheet_name='Leontief_Inverse_L')

        # Sector multipliers
        multipliers_df = pd.DataFrame({
            'Sector': sectors,
            'Code': sector_codes,
            'Output_Multiplier': L.sum(axis=0),
            'Direct_Effect': np.diag(L),
            'Indirect_Effect': L.sum(axis=0) - np.diag(L)
        })
        multipliers_df.to_excel(writer, sheet_name='Sector_Multipliers', index=False)

        # Metadata
        metadata = pd.DataFrame({
            'Parameter': [
                'Model', 'Country', 'Year', 'Sectors', 'Data_Type',
                'Scenario', 'Timestamp', 'Software'
            ],
            'Value': [
                'Leontief Input-Output', 'Uganda', '2019', n_sectors, 'Synthetic',
                'Infrastructure Investment', timestamp, 'Python/NumPy'
            ]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)

    print(f"✓ Excel file exported: {excel_path}")

    # Export main results to CSV
    csv_path = output_dir / f"uganda_results_{timestamp}.csv"
    results_main.to_csv(csv_path, index=False)
    print(f"✓ CSV file exported: {csv_path}")

    # Save Python pickle for programmatic access
    pickle_path = output_dir / f"uganda_results_{timestamp}.pkl"

    results_dict = {
        'metadata': {
            'model': 'Leontief Input-Output',
            'country': 'Uganda',
            'year': 2019,
            'data_type': 'Synthetic',
            'scenario': 'Infrastructure Investment',
            'timestamp': timestamp,
            'investment_amount': investment_amount,
            'shock_sector': 'Construction'
        },
        'baseline_data': {
            'sectors': sectors,
            'sector_codes': sector_codes,
            'A_matrix': A,
            'L_matrix': L,
            'y_baseline': y_baseline,
            'x_baseline': x_baseline,
            'employment_coef': employment_coef,
            'employment_baseline': employment_baseline,
            'value_added': value_added_by_sector,
            'gdp': total_gdp
        },
        'shock': {
            'delta_y': delta_y
        },
        'results': {
            'delta_x': delta_x,
            'delta_employment': delta_employment,
            'output_multiplier': total_multiplier,
            'employment_multiplier': employment_multiplier,
            'direct_output': direct_output,
            'indirect_output': indirect_output,
            'direct_jobs': direct_jobs,
            'indirect_jobs': indirect_jobs,
            'cost_per_job': cost_per_job
        },
        'dataframes': {
            'results_main': results_main,
            'summary_stats': summary_stats,
            'multipliers': multipliers_df
        }
    }

    with open(pickle_path, 'wb') as f:
        pickle.dump(results_dict, f)

    print(f"✓ Pickle file exported: {pickle_path}")

    print("\n" + "-"*80)
    print("All results exported successfully!")
    print("-"*80)
    print(f"\nOutput directory: {output_dir}")
    print(f"\nFiles created:")
    print(f"  1. {excel_path.name} - Comprehensive Excel workbook")
    print(f"  2. {csv_path.name} - Main results in CSV format")
    print(f"  3. {pickle_path.name} - Python data structure")
    print(f"  4. uganda_employment_impact_{timestamp}.png - Visualization")

# =============================================================================
# SECTION 10: INTERPRETATION GUIDE & NEXT STEPS
# =============================================================================

print("\n" + "="*80)
print("[Step 10/10] INTERPRETATION & NEXT STEPS")
print("="*80)

print("""
================================================================================
UNDERSTANDING YOUR RESULTS
================================================================================

1. OUTPUT MULTIPLIER
--------------------
""" + f"Value: {total_multiplier:.2f}" + """

This means every $1 invested in infrastructure generates $""" + f"{total_multiplier:.2f}" + """ of
total economic output across all sectors.

Interpretation:
• > 1.0 = Positive spillover effects (ALWAYS true in I-O models)
• 1.5-2.5 = Typical range for infrastructure in developing countries
• Higher = More interconnected economy, stronger supply chains

Your result """ + ("is typical" if 1.5 <= total_multiplier <= 2.5 else "is " +
                  ("below typical (weak linkages)" if total_multiplier < 1.5
                   else "above typical (strong linkages)")) + """

2. EMPLOYMENT MULTIPLIER
------------------------
""" + f"Value: {employment_multiplier:.1f} jobs per $M invested" + """

This means every $1 million invested creates """ + f"{employment_multiplier:.0f} total jobs." + """

Interpretation:
• Higher for labor-intensive sectors
• Varies by development level (higher in developing countries)
• Includes direct + all indirect jobs in supply chains

Cost per job: $""" + f"{cost_per_job:,.0f}" + """
""" + ("This is relatively low (good value)" if cost_per_job < 50000
      else "This is moderate" if cost_per_job < 100000
      else "This is relatively high") + """

3. DIRECT VS INDIRECT EFFECTS
------------------------------
""" + f"""
Direct effects:   {direct_output/delta_x.sum()*100:.1f}% of output, {direct_jobs/delta_employment.sum()*100:.1f}% of jobs
Indirect effects: {indirect_output/delta_x.sum()*100:.1f}% of output, {indirect_jobs/delta_employment.sum()*100:.1f}% of jobs
""" + """
The """ + f"{indirect_jobs/direct_jobs:.2f}" + """:1 ratio of indirect to direct jobs shows
""" + ("STRONG" if indirect_jobs/direct_jobs > 1.0 else "MODERATE" if indirect_jobs/direct_jobs > 0.5 else "WEAK") + """ supply chain linkages.

For every job created directly in Construction, """ + f"{indirect_jobs/direct_jobs:.1f}" + """
additional jobs are created in other sectors.

4. SECTORAL DISTRIBUTION
-------------------------
Top 3 sectors benefiting (by employment):
""")

if not USE_REAL_DATA:
    empl_ranking = sorted(zip(sectors, delta_employment), key=lambda x: x[1], reverse=True)
    for i, (sector, jobs) in enumerate(empl_ranking[:3], 1):
        print(f"  {i}. {sector}: {jobs:,.0f} jobs ({jobs/delta_employment.sum()*100:.1f}%)")

print("""
This distribution shows which sectors have the strongest:
• Supply linkages to Construction
• Labor intensity
• Importance for inclusive growth

================================================================================
POLICY IMPLICATIONS
================================================================================

1. ECONOMIC EFFICIENCY
   → Infrastructure investment has strong multiplier effects
   → Creates more economic activity than just direct spending
   → Justifies public investment even with budget constraints

2. EMPLOYMENT GENERATION
   → """ + f"Creates {employment_multiplier:.0f} jobs per $M" + """ invested
   → Strong job creation beyond construction sector
   → Particularly benefits labor-intensive sectors (agriculture, services)

3. POVERTY REDUCTION
   → Indirect jobs in agriculture and services
   → These sectors employ poor/vulnerable populations
   → Infrastructure investment = pro-poor growth strategy

4. SUPPLY CHAIN DEVELOPMENT
   → Stimulates local manufacturing and services
   → Encourages business development in supporting sectors
   → Can be enhanced with local content requirements

================================================================================
CAVEATS & LIMITATIONS
================================================================================

This analysis is STATIC and SHORT-RUN. It assumes:

1. ✗ No supply constraints (all sectors can expand freely)
   Reality: Some sectors may face capacity constraints

2. ✗ Fixed prices (no inflation or relative price changes)
   Reality: Demand increases may raise prices in some sectors

3. ✗ Linear relationships (constant returns to scale)
   Reality: Efficiency may change with scale

4. ✗ Fixed technology (A matrix constant)
   Reality: Technology may change over time

5. ✗ No feedback loops (employment → income → consumption)
   Reality: New wages create additional consumption demand

6. ✗ No time dynamics (immediate effects)
   Reality: Effects occur over multiple years

7. ✗ No crowding out (no opportunity cost of funds)
   Reality: Government investment may reduce private investment

FOR MORE REALISTIC ANALYSIS:
• Use full GLORIA MRIO data (169 countries, 120 sectors)
• Add price effects and substitution (MINDSET model)
• Include income-expenditure feedback loops
• Use Computable General Equilibrium (CGE) models
• Add dynamic/multi-period analysis

================================================================================
NEXT STEPS
================================================================================

1. SENSITIVITY ANALYSIS
   → Try different investment amounts
   → Test shocks to different sectors
   → Vary employment coefficients

   Run: python uganda_employment_impact_tutorial.py
   Then choose different scenarios when prompted

2. GET REAL GLORIA DATA
   → pymrio has downloaded the data structure
   → Parse and load actual Uganda data
   → Re-run analysis with full 120-sector detail

   See Section 2 for download instructions

3. EXTEND THE MODEL
   → Add household consumption feedback
   → Include price effects
   → Model multiple time periods
   → Add government budget constraints

4. USE FULL MINDSET MODEL
   → Run RunMINDSET.py for complete analysis
   → Includes energy substitution, trade effects, price changes
   → More realistic but more complex

5. COMPARE SCENARIOS
   → Infrastructure vs education vs health investment
   → Different regions within Uganda
   → COVID-19 demand shock (negative)

6. POLICY ANALYSIS
   → Local content requirements
   → Sector targeting for job creation
   → Optimal mix of investments

================================================================================
LEARNING RESOURCES
================================================================================

INPUT-OUTPUT ANALYSIS:
• Miller & Blair (2009): "Input-Output Analysis: Foundations and Extensions"
• Leontief (1986): "Input-Output Economics" (original text)

GLORIA DATABASE:
• Website: https://www.gloria-mrio.com/
• Documentation: https://www.gloria-mrio.com/docs

PYMRIO LIBRARY:
• Documentation: https://pymrio.readthedocs.io/
• Examples: https://pymrio.readthedocs.io/en/latest/notebooks/

MINDSET MODEL:
• Documentation folder in this repository
• SourceCode modules for implementation details

================================================================================
""")

print("\n" + "="*80)
print("TUTORIAL COMPLETE!")
print("="*80)

print(f"""
✓ You now understand the MINDSET employment impact methodology!

SUMMARY OF WHAT YOU LEARNED:
-----------------------------
1. How to download GLORIA data using pymrio
2. Technical coefficients (A matrix) - production recipes
3. Leontief inverse (L matrix) - total requirements with supply chains
4. Output impacts (Δx = L · Δy) - how shocks propagate
5. Employment impacts (ΔE = e · Δx) - job creation
6. Multiplier effects - direct vs indirect impacts
7. Policy interpretation - what the numbers mean

YOUR RESULTS:
-------------
• ${investment_amount:,.0f}M infrastructure investment
• ${delta_x.sum():,.0f}M total output generated (multiplier: {total_multiplier:.2f})
• {delta_employment.sum():,.0f} jobs created (multiplier: {employment_multiplier:.1f} per $M)
• Cost per job: ${cost_per_job:,.0f}

OUTPUTS SAVED:
--------------
📁 {output_dir}
   📊 uganda_results_{timestamp}.xlsx (comprehensive workbook)
   📄 uganda_results_{timestamp}.csv (main results)
   🐍 uganda_results_{timestamp}.pkl (Python data)
   📈 uganda_employment_impact_{timestamp}.png (visualization)

NEXT ACTIONS:
-------------
→ Review the Excel file for detailed results
→ Try different scenarios (re-run this script)
→ Download full GLORIA data for realistic analysis
→ Explore the SourceCode modules for advanced features
→ Read the Documentation folder for technical details

Thank you for using this tutorial! For questions about MINDSET methodology,
refer to the Documentation folder or contact the model developers.
================================================================================
""")
