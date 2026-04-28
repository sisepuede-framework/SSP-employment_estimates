"""
================================================================================
UGANDA EMPLOYMENT IMPACT TUTORIAL - SYNTHETIC DATA VERSION
Automatic execution with synthetic 5-sector economy
================================================================================

This script runs the complete employment impact analysis using a simplified
synthetic Uganda economy. Perfect for learning the methodology!

Author: Fernando Esteves
Date: March 2026
================================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from pathlib import Path
import pickle

print("="*80)
print("UGANDA EMPLOYMENT IMPACT ANALYSIS - SYNTHETIC DATA")
print("="*80)

# =============================================================================
# SETUP
# =============================================================================

cwd = Path(os.getcwd())
output_dir = cwd.parent / "GLORIA_results"
output_dir.mkdir(exist_ok=True)

print("\n[SETUP]")
print(f"Working directory: {cwd}")
print(f"Output directory: {output_dir}")

# =============================================================================
# STEP 1: CREATE SYNTHETIC UGANDA ECONOMY
# =============================================================================

print("\n" + "="*80)
print("[STEP 1/8] CREATING SYNTHETIC UGANDA ECONOMY")
print("="*80)

sectors = ['Agriculture', 'Manufacturing', 'Construction', 'Services', 'Energy']
sector_codes = ['AGR', 'MAN', 'CON', 'SER', 'ENE']
n_sectors = len(sectors)

print(f"\nSectors: {n_sectors}")
for i, (code, name) in enumerate(zip(sector_codes, sectors)):
    print(f"  {i+1}. {code} - {name}")

# =============================================================================
# STEP 2: TECHNICAL COEFFICIENTS MATRIX (A)
# =============================================================================

print("\n" + "="*80)
print("[STEP 2/8] TECHNICAL COEFFICIENTS MATRIX (A)")
print("="*80)

print("""
The A matrix shows inputs needed per $1 of output.
A[i,j] = input from sector i needed by sector j to produce $1 output
""")

A = np.array([
    # Inputs needed per $1 output in:
    # AGR   MAN   CON   SER   ENE
    [0.10, 0.15, 0.05, 0.03, 0.02],  # from Agriculture
    [0.05, 0.20, 0.25, 0.05, 0.10],  # from Manufacturing
    [0.02, 0.08, 0.15, 0.03, 0.05],  # from Construction
    [0.08, 0.12, 0.10, 0.20, 0.08],  # from Services
    [0.03, 0.10, 0.05, 0.05, 0.25]   # from Energy
])

A_df = pd.DataFrame(A, index=sector_codes, columns=sector_codes)
print("\nTechnical Coefficients Matrix (A):")
print(A_df.round(3))

col_sums = A.sum(axis=0)
print("\nValue added per $1 output:")
for i, (code, sum_val) in enumerate(zip(sector_codes, col_sums)):
    print(f"  {code}: ${1-sum_val:.3f}")

# =============================================================================
# STEP 3: LEONTIEF INVERSE MATRIX (L)
# =============================================================================

print("\n" + "="*80)
print("[STEP 3/8] LEONTIEF INVERSE MATRIX (L = (I-A)^-1)")
print("="*80)

print("""
The Leontief inverse captures all direct and indirect effects.
L[i,j] = total output from sector i needed when final demand for j increases by $1
""")

I = np.eye(n_sectors)
L = np.linalg.inv(I - A)

L_df = pd.DataFrame(L, index=sector_codes, columns=sector_codes)
print("\nLeontief Inverse Matrix (L):")
print(L_df.round(3))

print("\nOutput multipliers (total output per $1 final demand):")
for i, (code, sector) in enumerate(zip(sector_codes, sectors)):
    multiplier = L[:, i].sum()
    print(f"  {code} - {sector:15s}: {multiplier:.3f}")

# =============================================================================
# STEP 4: BASELINE FINAL DEMAND (y)
# =============================================================================

print("\n" + "="*80)
print("[STEP 4/8] BASELINE FINAL DEMAND")
print("="*80)

print("""
Final demand = Household consumption + Government + Investment + Exports
Values in million USD (2019 prices)
""")

y_baseline = np.array([3500, 2000, 1200, 4000, 800])

demand_df = pd.DataFrame({
    'Sector': sectors,
    'Code': sector_codes,
    'Final Demand ($M)': y_baseline,
    'Share (%)': (y_baseline / y_baseline.sum() * 100).round(1)
})

print("\nBaseline Final Demand:")
print(demand_df.to_string(index=False))
print(f"\nTotal: ${y_baseline.sum():,.0f}M")

# =============================================================================
# STEP 5: BASELINE GROSS OUTPUT (x = L·y)
# =============================================================================

print("\n" + "="*80)
print("[STEP 5/8] BASELINE GROSS OUTPUT")
print("="*80)

x_baseline = L @ y_baseline

intermediate_use = A @ x_baseline
value_added = x_baseline - intermediate_use
gdp = value_added.sum()

output_df = pd.DataFrame({
    'Sector': sectors,
    'Code': sector_codes,
    'Final Demand': y_baseline,
    'Gross Output': x_baseline.round(0),
    'Value Added': value_added.round(0)
})

print("\nBaseline Economic Structure:")
print(output_df.to_string(index=False))
print(f"\nTotal GDP: ${gdp:,.0f}M")

# =============================================================================
# STEP 6: EMPLOYMENT COEFFICIENTS & BASELINE EMPLOYMENT
# =============================================================================

print("\n" + "="*80)
print("[STEP 6/8] EMPLOYMENT STRUCTURE")
print("="*80)

employment_coef = np.array([280, 95, 150, 220, 50])  # workers per $M output
employment_baseline = employment_coef * x_baseline

empl_df = pd.DataFrame({
    'Sector': sectors,
    'Code': sector_codes,
    'Coef (jobs/$M)': employment_coef,
    'Output ($M)': x_baseline.round(0),
    'Employment': employment_baseline.round(0),
    'Share (%)': (employment_baseline / employment_baseline.sum() * 100).round(1)
})

print("\nBaseline Employment:")
print(empl_df.to_string(index=False))
print(f"\nTotal Employment: {employment_baseline.sum():,.0f} workers")

# =============================================================================
# STEP 7: SIMULATE INFRASTRUCTURE INVESTMENT SHOCK
# =============================================================================

print("\n" + "="*80)
print("[STEP 7/8] INFRASTRUCTURE INVESTMENT SCENARIO")
print("="*80)

investment_amount = 800  # $800 million

print(f"""
SCENARIO: Infrastructure Investment Program
- Investment: ${investment_amount:,.0f} million
- Sector: Construction
- Type: Roads, bridges, schools, hospitals
""")

# Create shock vector
delta_y = np.zeros(n_sectors)
delta_y[2] = investment_amount  # Construction

# Calculate output impact: Δx = L·Δy
delta_x = L @ delta_y
x_new = x_baseline + delta_x

# Calculate employment impact: ΔE = e·Δx
delta_employment = employment_coef * delta_x
employment_new = employment_baseline + delta_employment

# Multipliers
output_multiplier = delta_x.sum() / investment_amount
employment_multiplier = delta_employment.sum() / investment_amount
cost_per_job = (investment_amount * 1e6) / delta_employment.sum()

# Direct vs indirect
direct_output = delta_x[2]
indirect_output = delta_x.sum() - direct_output
direct_jobs = delta_employment[2]
indirect_jobs = delta_employment.sum() - direct_jobs

print("\n" + "-"*80)
print("IMPACT RESULTS")
print("-"*80)

impact_df = pd.DataFrame({
    'Sector': sectors,
    'Code': sector_codes,
    'ΔOutput ($M)': delta_x.round(1),
    'ΔEmployment': delta_employment.round(0),
    '% of Total Output': (delta_x / delta_x.sum() * 100).round(1),
    '% of Total Jobs': (delta_employment / delta_employment.sum() * 100).round(1)
})

print("\nSectoral Impacts:")
print(impact_df.to_string(index=False))

print(f"\n{'='*60}")
print("SUMMARY STATISTICS")
print(f"{'='*60}")
print(f"Investment:              ${investment_amount:,.0f}M")
print(f"Total Output Impact:     ${delta_x.sum():,.1f}M")
print(f"Output Multiplier:       {output_multiplier:.2f}")
print(f"Total Jobs Created:      {delta_employment.sum():,.0f}")
print(f"Employment Multiplier:   {employment_multiplier:.1f} jobs/$M")
print(f"Cost per Job:            ${cost_per_job:,.0f}")
print(f"\n→ Every $1M invested creates {employment_multiplier:.0f} jobs")
print(f"→ Every $1 invested generates ${output_multiplier:.2f} of output")

print(f"\n{'='*60}")
print("DIRECT vs INDIRECT EFFECTS")
print(f"{'='*60}")
print(f"Direct Output:           ${direct_output:,.1f}M ({direct_output/delta_x.sum()*100:.1f}%)")
print(f"Indirect Output:         ${indirect_output:,.1f}M ({indirect_output/delta_x.sum()*100:.1f}%)")
print(f"Direct Jobs:             {direct_jobs:,.0f} ({direct_jobs/delta_employment.sum()*100:.1f}%)")
print(f"Indirect Jobs:           {indirect_jobs:,.0f} ({indirect_jobs/delta_employment.sum()*100:.1f}%)")

# =============================================================================
# STEP 8: VISUALIZATIONS
# =============================================================================

print("\n" + "="*80)
print("[STEP 8/8] CREATING VISUALIZATIONS")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle(f'Uganda Infrastructure Investment Impact Analysis\n'
             f'${investment_amount:,.0f}M Investment in Construction',
             fontsize=14, fontweight='bold')

# Plot 1: Output Impact
ax1 = axes[0, 0]
colors1 = ['green' if i == 2 else 'steelblue' for i in range(n_sectors)]
bars1 = ax1.bar(range(n_sectors), delta_x, color=colors1, alpha=0.7, edgecolor='black')
ax1.set_xticks(range(n_sectors))
ax1.set_xticklabels(sector_codes, fontweight='bold')
ax1.set_ylabel('Output Change ($M)', fontweight='bold')
ax1.set_title('Output Impact by Sector', fontweight='bold')
ax1.grid(axis='y', alpha=0.3)
for bar, val in zip(bars1, delta_x):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
            f'${val:.0f}M', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 2: Employment Impact
ax2 = axes[0, 1]
colors2 = ['green' if i == 2 else 'coral' for i in range(n_sectors)]
bars2 = ax2.bar(range(n_sectors), delta_employment, color=colors2, alpha=0.7, edgecolor='black')
ax2.set_xticks(range(n_sectors))
ax2.set_xticklabels(sector_codes, fontweight='bold')
ax2.set_ylabel('Employment Change (jobs)', fontweight='bold')
ax2.set_title('Employment Impact by Sector', fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
for bar, val in zip(bars2, delta_employment):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
            f'{val:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 3: Output Distribution (Pie)
ax3 = axes[0, 2]
colors3 = ['green' if i == 2 else plt.cm.Blues(0.3 + i*0.15) for i in range(n_sectors)]
wedges, texts, autotexts = ax3.pie(delta_x, labels=sector_codes, autopct='%1.1f%%',
                                    colors=colors3, startangle=90)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax3.set_title(f'Output Distribution\nTotal: ${delta_x.sum():.0f}M', fontweight='bold')

# Plot 4: Employment Distribution (Pie)
ax4 = axes[1, 0]
colors4 = ['green' if i == 2 else plt.cm.Oranges(0.3 + i*0.15) for i in range(n_sectors)]
wedges, texts, autotexts = ax4.pie(delta_employment, labels=sector_codes, autopct='%1.1f%%',
                                    colors=colors4, startangle=90)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax4.set_title(f'Employment Distribution\nTotal: {delta_employment.sum():,.0f} jobs', fontweight='bold')

# Plot 5: Direct vs Indirect
ax5 = axes[1, 1]
x_pos = np.arange(2)
width = 0.35
direct_vals = [direct_output, direct_jobs]
indirect_vals = [indirect_output, indirect_jobs]
bars5a = ax5.bar(x_pos - width/2, direct_vals, width, label='Direct',
                 color='green', alpha=0.7, edgecolor='black')
bars5b = ax5.bar(x_pos + width/2, indirect_vals, width, label='Indirect',
                 color='steelblue', alpha=0.7, edgecolor='black')
ax5.set_ylabel('Impact', fontweight='bold')
ax5.set_title('Direct vs Indirect Effects', fontweight='bold')
ax5.set_xticks(x_pos)
ax5.set_xticklabels(['Output\n($M)', 'Employment\n(jobs)'], fontweight='bold')
ax5.legend()
ax5.grid(axis='y', alpha=0.3)

# Plot 6: Key Metrics
ax6 = axes[1, 2]
ax6.axis('off')
metrics_text = f"""
KEY METRICS

Investment
• Amount: ${investment_amount:,.0f}M
• Sector: Construction

Output Effects
• Total: ${delta_x.sum():,.0f}M
• Multiplier: {output_multiplier:.2f}
• Direct: {direct_output/delta_x.sum()*100:.0f}%
• Indirect: {indirect_output/delta_x.sum()*100:.0f}%

Employment Effects
• Total: {delta_employment.sum():,.0f} jobs
• Multiplier: {employment_multiplier:.1f} jobs/$M
• Direct: {direct_jobs/delta_employment.sum()*100:.0f}%
• Indirect: {indirect_jobs/delta_employment.sum()*100:.0f}%

Cost per Job: ${cost_per_job:,.0f}
"""
ax6.text(0.1, 0.95, metrics_text, transform=ax6.transAxes,
         fontsize=10, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Save figure
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
figure_path = output_dir / f"uganda_impact_{timestamp}.png"
plt.savefig(figure_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Visualization saved: {figure_path}")

# =============================================================================
# EXPORT RESULTS
# =============================================================================

print("\n" + "="*80)
print("EXPORTING RESULTS")
print("="*80)

# Main results DataFrame
results_df = pd.DataFrame({
    'Sector': sectors,
    'Code': sector_codes,
    'Baseline_FinalDemand': y_baseline,
    'Baseline_GrossOutput': x_baseline.round(2),
    'Baseline_Employment': employment_baseline.round(0),
    'Demand_Shock': delta_y,
    'Output_Change': delta_x.round(2),
    'Employment_Change': delta_employment.round(0),
    'New_Output': x_new.round(2),
    'New_Employment': employment_new.round(0)
})

# Export to Excel
excel_path = output_dir / f"uganda_results_{timestamp}.xlsx"

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    results_df.to_excel(writer, sheet_name='Results', index=False)

    summary_df = pd.DataFrame({
        'Metric': ['Investment', 'Output Multiplier', 'Employment Multiplier',
                   'Total Jobs Created', 'Cost per Job', 'Direct Jobs', 'Indirect Jobs'],
        'Value': [investment_amount, output_multiplier, employment_multiplier,
                 delta_employment.sum(), cost_per_job, direct_jobs, indirect_jobs]
    })
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

    A_df.to_excel(writer, sheet_name='Tech_Coefficients')
    L_df.to_excel(writer, sheet_name='Leontief_Inverse')

print(f"✓ Excel exported: {excel_path}")

# CSV export
csv_path = output_dir / f"uganda_results_{timestamp}.csv"
results_df.to_csv(csv_path, index=False)
print(f"✓ CSV exported: {csv_path}")

# Pickle export
pickle_path = output_dir / f"uganda_results_{timestamp}.pkl"
results_dict = {
    'parameters': {'investment': investment_amount, 'sector': 'Construction'},
    'matrices': {'A': A, 'L': L},
    'baseline': {'y': y_baseline, 'x': x_baseline, 'employment': employment_baseline},
    'impacts': {'delta_y': delta_y, 'delta_x': delta_x, 'delta_employment': delta_employment},
    'multipliers': {'output': output_multiplier, 'employment': employment_multiplier}
}
with open(pickle_path, 'wb') as f:
    pickle.dump(results_dict, f)
print(f"✓ Pickle exported: {pickle_path}")

# =============================================================================
# COMPLETION
# =============================================================================

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)

print(f"""
✓ Uganda employment impact analysis finished successfully!

KEY FINDINGS:
-------------
• ${investment_amount:,.0f}M infrastructure investment in Construction
• Generates ${delta_x.sum():,.1f}M total output (multiplier: {output_multiplier:.2f})
• Creates {delta_employment.sum():,.0f} total jobs (multiplier: {employment_multiplier:.1f} jobs/$M)
• Cost per job: ${cost_per_job:,.0f}
• Direct jobs: {direct_jobs:,.0f} ({direct_jobs/delta_employment.sum()*100:.0f}%)
• Indirect jobs: {indirect_jobs:,.0f} ({indirect_jobs/delta_employment.sum()*100:.0f}%)

OUTPUTS SAVED:
--------------
📊 {excel_path.name}
📄 {csv_path.name}
🐍 {pickle_path.name}
📈 {figure_path.name}

LOCATION:
---------
{output_dir}

INTERPRETATION:
---------------
• Strong multiplier effects (output: {output_multiplier:.2f}, employment: {employment_multiplier:.1f})
• For every $1M invested, {employment_multiplier:.0f} jobs are created
• {indirect_jobs/direct_jobs:.1f}x more indirect jobs than direct jobs
• Agriculture and Services benefit significantly (labor-intensive)
• Demonstrates value of infrastructure investment for inclusive growth

NEXT STEPS:
-----------
1. Review the Excel file for detailed results
2. Examine visualizations (close plot window)
3. Try different investment amounts or sectors
4. When ready, download real GLORIA data for full 120-sector analysis
5. Use this methodology in your dissertation!

YOU NOW UNDERSTAND:
-------------------
✓ Input-Output model fundamentals (A and L matrices)
✓ How demand shocks propagate through the economy
✓ Employment multiplier calculation
✓ Direct vs indirect effects
✓ The MINDSET employment impact methodology

This is the EXACT methodology used in the full MINDSET model,
just with 5 sectors instead of 120!
""")

# Show the plot
print("\n" + "="*80)
print("Displaying visualization...")
print("(Close the plot window to exit)")
print("="*80)

plt.show()

print("\n✓ Script complete. All results saved.")
print(f"Output directory: {output_dir}\n")
