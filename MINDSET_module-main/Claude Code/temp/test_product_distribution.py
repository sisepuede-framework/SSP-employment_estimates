#!/usr/bin/env python
"""
Test Script - Product Distribution Dataset Builder
This runs key validation checks on the actual data before full processing
"""

import pandas as pd
import numpy as np
import os

# Configuration
DATA_PATH = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"
COST_STRUCTURE_PATH = os.path.join(DATA_PATH, "Cost Structure")
CROSSWALK_FILE = os.path.join(DATA_PATH, "GLORIA-Eora26 - Crosswalk.xlsx")
COUNTRIES = ["BGR", "BLZ", "EGY", "LBY", "MAR", "MEX", "UGA"]

print("="*80)
print("TESTING PRODUCT DISTRIBUTION DATASET BUILDER")
print("="*80)

# ==============================================================================
# TEST 1: Load Crosswalk
# ==============================================================================
print("\nTEST 1: Loading Crosswalk")
print("-"*80)

try:
    crosswalk_wide = pd.read_excel(CROSSWALK_FILE, sheet_name="Eora26 - GLORIA")
    print("SUCCESS: Loaded crosswalk")
    print(f"  Dimensions: {crosswalk_wide.shape[0]} rows × {crosswalk_wide.shape[1]} columns")
    print(f"  Column names: {', '.join(crosswalk_wide.columns[:5])}...")

    # Identify sector columns
    sector_cols = [col for col in crosswalk_wide.columns
                   if col not in ['Products', 'Codes', 'Lfd_Nr']]
    print(f"  Sector columns identified: {len(sector_cols)}")
    print(f"  Sectors: {', '.join(sector_cols[:5])}...")

except Exception as e:
    print(f"ERROR loading crosswalk: {e}")
    exit(1)

# ==============================================================================
# TEST 2: Transform Crosswalk to Long
# ==============================================================================
print("\nTEST 2: Transform Crosswalk to Long Format")
print("-"*80)

try:
    # Melt to long format
    crosswalk_long = crosswalk_wide.melt(
        id_vars=['Products'],
        value_vars=sector_cols,
        var_name='Sector',
        value_name='linked'
    )

    # Keep only links (where value = 1)
    crosswalk_long = crosswalk_long[crosswalk_long['linked'] == 1][['Products', 'Sector']]

    print("SUCCESS: Transformed to long format")
    print(f"  Rows: {len(crosswalk_long)} (Product-Sector pairs)")
    print(f"  Unique products: {crosswalk_long['Products'].nunique()}")
    print(f"  Unique sectors: {crosswalk_long['Sector'].nunique()}")

    print("\nSample Product-Sector links:")
    print(crosswalk_long.head(10).to_string())

    # Count products per sector
    products_per_sector = crosswalk_long.groupby('Sector').size().reset_index(name='n_products')

    print("\nProducts per sector:")
    print(products_per_sector.to_string())

    # Add to crosswalk
    crosswalk_long = crosswalk_long.merge(products_per_sector, on='Sector')

except Exception as e:
    print(f"ERROR transforming crosswalk: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ==============================================================================
# TEST 3: Load Distribution Files (Test with 1 country first)
# ==============================================================================
print("\n" + "="*80)
print("TEST 3: Loading Distribution Files")
print("-"*80)

test_country = COUNTRIES[0]
print(f"Testing with: {test_country}")

try:
    file_path = os.path.join(COST_STRUCTURE_PATH, f"cost_str_{test_country}.xlsx")

    if not os.path.exists(file_path):
        print(f"  ERROR: File not found: {file_path}")
        exit(1)

    print(f"  Loading: {os.path.basename(file_path)}")

    test_dist = pd.read_excel(file_path)
    test_dist['Country'] = test_country

    print("SUCCESS: Loaded distribution file")
    print(f"  Dimensions: {test_dist.shape[0]} rows × {test_dist.shape[1]} columns")
    print(f"  Columns: {', '.join(test_dist.columns)}")

    print("\nFirst 10 rows:")
    print(test_dist.head(10).to_string())

    # Check required columns
    required_cols = ['Sector', 'strategy_id', 'value']
    missing = [col for col in required_cols if col not in test_dist.columns]

    if missing:
        print(f"\nERROR: Missing required columns: {', '.join(missing)}")
        exit(1)
    else:
        print("\nSUCCESS: All required columns present")

    # Check unique values
    print(f"\n  Unique strategies: {test_dist['strategy_id'].nunique()}")
    print(f"  Unique sectors: {test_dist['Sector'].nunique()}")
    print(f"  Value range: {test_dist['value'].min():.6f} to {test_dist['value'].max():.6f}")

    # Check sums
    sum_check = test_dist.groupby('strategy_id')['value'].sum().reset_index(name='total')

    print("\n  Sum of values per strategy:")
    print(f"    Mean: {sum_check['total'].mean():.6f}")
    print(f"    Min: {sum_check['total'].min():.6f}")
    print(f"    Max: {sum_check['total'].max():.6f}")

    bad_sums = sum_check[np.abs(sum_check['total'] - 1.0) > 1e-6]
    if len(bad_sums) > 0:
        print(f"\n  WARNING: {len(bad_sums)} strategies don't sum to 1.0:")
        print(bad_sums.head().to_string())
    else:
        print("\n  SUCCESS: All strategies sum to 1.0")

except Exception as e:
    print(f"ERROR loading distribution: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ==============================================================================
# TEST 4: Check Sector Name Matching
# ==============================================================================
print("\n" + "="*80)
print("TEST 4: Check Sector Name Matching")
print("-"*80)

try:
    sectors_crosswalk = set(crosswalk_long['Sector'].unique())
    sectors_distribution = set(test_dist['Sector'].unique())

    print(f"Sectors in crosswalk: {len(sectors_crosswalk)}")
    print(f"Sectors in distribution: {len(sectors_distribution)}")

    in_crosswalk_not_dist = sectors_crosswalk - sectors_distribution
    in_dist_not_crosswalk = sectors_distribution - sectors_crosswalk

    if in_crosswalk_not_dist:
        print("\nWARNING: Sectors in crosswalk but NOT in distribution:")
        for sector in sorted(in_crosswalk_not_dist):
            print(f"  - {sector}")

    if in_dist_not_crosswalk:
        print("\nWARNING: Sectors in distribution but NOT in crosswalk:")
        for sector in sorted(in_dist_not_crosswalk):
            print(f"  - {sector}")

    if not in_crosswalk_not_dist and not in_dist_not_crosswalk:
        print("\nSUCCESS: All sector names match perfectly!")

except Exception as e:
    print(f"ERROR checking sector names: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# TEST 5: Test Merge and Allocation (Small Sample)
# ==============================================================================
print("\n" + "="*80)
print("TEST 5: Test Merge and Allocation")
print("-"*80)

try:
    # Test with first strategy only
    test_strategy = test_dist['strategy_id'].iloc[0]
    print(f"Testing with strategy: {test_strategy}")

    test_subset = test_dist[test_dist['strategy_id'] == test_strategy].copy()

    # Merge with crosswalk
    test_merge = test_subset.merge(
        crosswalk_long,
        left_on='Sector',
        right_on='Sector',
        how='left'
    )

    # Remove rows where product is NaN (sectors not in crosswalk)
    test_merge = test_merge[test_merge['Products'].notna()]

    # Calculate product-level values
    test_merge['value_sector'] = test_merge['value']
    test_merge['value_product'] = test_merge['value_sector'] / test_merge['n_products']

    print("SUCCESS: Merged and allocated")
    print(f"  Merged rows: {len(test_merge)}")
    print(f"  Unique products: {test_merge['Products'].nunique()}")

    print("\nSample allocated values:")
    sample = test_merge[['Country', 'strategy_id', 'Products', 'Sector', 'n_products', 'value_product']].head(15)
    print(sample.to_string())

    # Check sum
    total_value_product = test_merge['value_product'].sum()
    print(f"\nTotal Value_Product for this strategy: {total_value_product:.10f}")
    print(f"Should be 1.0. Difference: {abs(total_value_product - 1.0):.10e}")

    if abs(total_value_product - 1.0) < 1e-6:
        print("SUCCESS: Values sum to 1.0!")
    else:
        print("WARNING: Values do NOT sum to 1.0")
        print(f"  Missing: {1.0 - total_value_product:.6f}")

except Exception as e:
    print(f"ERROR during merge/allocation: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# TEST 6: Check Multi-Sector Products
# ==============================================================================
print("\n" + "="*80)
print("TEST 6: Check Multi-Sector Products")
print("-"*80)

try:
    # Check for products appearing multiple times
    multi_check = test_merge.groupby('Products').agg({
        'Sector': lambda x: ' + '.join(x),
        'value_product': 'sum',
        'Country': 'size'
    }).rename(columns={'Country': 'n_sectors'})

    multi_check = multi_check[multi_check['n_sectors'] > 1]

    if len(multi_check) > 0:
        print(f"Found {len(multi_check)} products linked to multiple sectors")
        print(multi_check.head(10).to_string())
        print("\nAfter summing, these products will have higher values")
    else:
        print("No multi-sector products found in this test")

except Exception as e:
    print(f"ERROR checking multi-sector: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# TEST 7: Check All Country Files
# ==============================================================================
print("\n" + "="*80)
print("TEST 7: Check All Country Files")
print("-"*80)

for country in COUNTRIES:
    file_path = os.path.join(COST_STRUCTURE_PATH, f"cost_str_{country}.xlsx")

    if os.path.exists(file_path):
        print(f"  {country}: FOUND")
    else:
        print(f"  {country}: NOT FOUND ({file_path})")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

print("\nAll critical tests completed.")
print("\nNext steps:")
print("  1. Review any warnings above")
print("  2. If all looks good, run the full Rmd file in RStudio/Positron")
print("  3. Check final output for validation")
print("\n" + "="*80)
