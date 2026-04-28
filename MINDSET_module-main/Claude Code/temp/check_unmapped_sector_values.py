"""
Check how much value is in the 3 unmapped sectors in cost structure files
"""
import pandas as pd
import os
import numpy as np

COST_STRUCTURE_PATH = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data\Cost Structure"
COUNTRIES = ["BGR", "BLZ", "EGY", "LBY", "MAR", "MEX", "UGA"]
UNMAPPED_SECTORS = ["Wholesale Trade", "Retail Trade", "Re-export & Re-import"]

print("="*80)
print("CHECKING VALUE IN UNMAPPED SECTORS")
print("="*80)

all_results = []

for country in COUNTRIES:
    file_path = os.path.join(COST_STRUCTURE_PATH, f"cost_str_{country}.xlsx")

    if not os.path.exists(file_path):
        print(f"\n{country}: File not found - SKIP")
        continue

    print(f"\n{country}: Loading...")

    try:
        df = pd.read_excel(file_path)

        # Check for unmapped sectors
        unmapped_data = df[df['Sector'].isin(UNMAPPED_SECTORS)]

        if len(unmapped_data) > 0:
            # Calculate stats per strategy
            stats = unmapped_data.groupby('strategy_id')['value'].sum().reset_index()
            stats.columns = ['strategy_id', 'unmapped_value']
            stats['Country'] = country

            all_results.append(stats)

            print(f"  Strategies with unmapped sectors: {len(stats)}")
            print(f"  Unmapped value range: {stats['unmapped_value'].min():.4f} to {stats['unmapped_value'].max():.4f}")
            print(f"  Mean unmapped value: {stats['unmapped_value'].mean():.4f}")
        else:
            print(f"  No unmapped sectors found (good!)")

    except Exception as e:
        print(f"  ERROR: {e}")

if all_results:
    print("\n" + "="*80)
    print("SUMMARY ACROSS ALL COUNTRIES")
    print("="*80)

    combined = pd.concat(all_results, ignore_index=True)

    print(f"\nTotal (Country, Strategy) combinations with unmapped sectors: {len(combined)}")
    print(f"\nUnmapped value statistics:")
    print(f"  Min:  {combined['unmapped_value'].min():.4f}")
    print(f"  Q1:   {combined['unmapped_value'].quantile(0.25):.4f}")
    print(f"  Mean: {combined['unmapped_value'].mean():.4f}")
    print(f"  Q3:   {combined['unmapped_value'].quantile(0.75):.4f}")
    print(f"  Max:  {combined['unmapped_value'].max():.4f}")

    print(f"\nPercentage of strategy value lost:")
    print(f"  (This is how much less than 1.0 the product-level sums will be)")

    # Count by severity
    severe = combined[combined['unmapped_value'] > 0.10]
    moderate = combined[(combined['unmapped_value'] > 0.05) & (combined['unmapped_value'] <= 0.10)]
    minor = combined[combined['unmapped_value'] <= 0.05]

    print(f"\n  Severe (> 10% lost):    {len(severe):3} cases")
    print(f"  Moderate (5-10% lost):  {len(moderate):3} cases")
    print(f"  Minor (<= 5% lost):     {len(minor):3} cases")

    if len(severe) > 0:
        print(f"\n  WARNING: {len(severe)} strategies will lose > 10% of value!")
        print(f"  Recommendation: Map these sectors to products")
    elif len(moderate) > 0:
        print(f"\n  CAUTION: {len(moderate)} strategies will lose 5-10% of value")
        print(f"  Recommendation: Consider mapping or document as limitation")
    else:
        print(f"\n  ACCEPTABLE: All strategies lose < 5% of value")
        print(f"  Can proceed with documentation as limitation")

    # Show top 10 worst cases
    print("\n" + "="*80)
    print("TOP 10 STRATEGIES WITH HIGHEST UNMAPPED VALUES")
    print("="*80)

    worst = combined.nlargest(10, 'unmapped_value')
    print(worst.to_string(index=False))

else:
    print("\n" + "="*80)
    print("RESULT: No unmapped sectors have values in any cost structure file!")
    print("="*80)
    print("\nThis means you can proceed without any issues.")
    print("The 3 unmapped sectors have zero values across all strategies.")

print("\n" + "="*80)
