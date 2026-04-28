"""
Quick check: Which Eora26 sectors have NO products mapped?
"""
import pandas as pd

# Load crosswalk
CROSSWALK_FILE = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data\GLORIA-Eora26 - Crosswalk.xlsx"

crosswalk_wide = pd.read_excel(CROSSWALK_FILE, sheet_name="Eora26 - GLORIA")

# Get all sector columns (exclude Products, Codes, Lfd_Nr)
sector_cols = [col for col in crosswalk_wide.columns
               if col not in ['Products', 'Codes', 'Lfd_Nr']]

print("="*80)
print("EORA26 SECTOR MAPPING CHECK")
print("="*80)

print(f"\nTotal Eora26 sectors in crosswalk: {len(sector_cols)}")
print("\nAll sector names:")
for i, sector in enumerate(sector_cols, 1):
    print(f"  {i:2}. {sector}")

# Count products per sector
print("\n" + "="*80)
print("PRODUCTS PER SECTOR")
print("="*80)

sector_counts = {}
for sector in sector_cols:
    count = crosswalk_wide[sector].sum()
    sector_counts[sector] = int(count)

# Sort by count
sorted_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)

print(f"\nSectors with products ({sum(1 for s, c in sorted_sectors if c > 0)}):")
for sector, count in sorted_sectors:
    if count > 0:
        print(f"  {sector:55} : {count:3} products")

print(f"\n{'='*80}")
print("UNMAPPED SECTORS (Zero products)")
print("="*80)

unmapped = [sector for sector, count in sorted_sectors if count == 0]

if unmapped:
    print(f"\nFound {len(unmapped)} sectors with NO products mapped:")
    for i, sector in enumerate(unmapped, 1):
        print(f"  {i}. {sector}")

    print(f"\n⚠️  WARNING: Values for these sectors will NOT be allocated to products!")
    print(f"   This will cause Value_Product sums to be < 1.0")
else:
    print("\n✓ All sectors have at least one product mapped!")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

if unmapped:
    print("\nOption 1: Update crosswalk to map these sectors to products")
    print("  - Find appropriate GLORIA products for these sectors")
    print("  - Add 1s in the crosswalk matrix")
    print()
    print("Option 2: Check if these sectors have significant values")
    print("  - If values are small (< 1%), might be acceptable to skip")
    print("  - Document as limitation")
    print()
    print("Option 3: Create generic products for these sectors")
    print("  - Add rows for 'Wholesale Trade Services', 'Retail Trade Services'")
    print("  - Map exclusively to their respective sectors")
else:
    print("\nNo action needed - all sectors mapped!")

print("\n" + "="*80)
