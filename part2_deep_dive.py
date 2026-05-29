import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import sys
sys.stdout.reconfigure(encoding='utf-8')

ab    = pd.read_csv('data/ab_test_results.csv')
sales = pd.read_csv('data/monthly_sales.csv')
cust  = pd.read_csv('data/customer_segments.csv')

NAVY, GREEN, CORAL = '#1E2761', '#2d7a2d', '#F96167'

print("="*60)
print("PART 2 — DEEP DIVE ANALYSIS")
print("="*60)

# Revenue lift
rev = ab.groupby('group')['revenue_usd'].agg(['mean','sum'])
lift = (rev.loc['Treatment','mean'] / rev.loc['Control','mean'] - 1) * 100
print(f"\n  Revenue lift (Treatment vs Control): {lift:+.1f}%")
print(f"  Control avg  : ${rev.loc['Control','mean']:.2f}")
print(f"  Treatment avg: ${rev.loc['Treatment','mean']:.2f}")

# MoM growth
sales['mom_pct'] = sales['monthly_revenue'].pct_change() * 100
sales['cumulative'] = sales['monthly_revenue'].cumsum()
print("\n  Month-over-Month Growth:")
for _, row in sales.iterrows():
    g = f"{row['mom_pct']:+.1f}%" if not pd.isna(row['mom_pct']) else "—"
    print(f"    {row['month']:8s}: ${row['monthly_revenue']:>7,.0f}   MoM {g}")

# LTV
cust['ltv'] = cust['annual_spend'] * cust['loyalty_years'].clip(1)
ltv_seg = cust.groupby('segment')['ltv'].agg(['median','mean']).round(2)
ltv_seg.columns = ['Median LTV', 'Mean LTV']
print(f"\n  Customer LTV by Segment:\n{ltv_seg}")

# ── Figure ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle('Part 2 — Deep Dive Analysis', fontsize=16, fontweight='bold')
plt.subplots_adjust(hspace=0.42, wspace=0.35)

# 1. Revenue by device & group
ax1 = axes[0,0]
rev_d = ab.groupby(['device','group'])['revenue_usd'].mean().unstack()
rev_d.plot(kind='bar', ax=ax1, color=[CORAL, GREEN], edgecolor='white', rot=20)
ax1.set_title('Avg Revenue per User by Device', fontweight='bold')
ax1.set_xlabel(''); ax1.set_ylabel('Avg Revenue ($)')
ax1.legend(title='Group'); ax1.grid(axis='y', alpha=0.3)
ax1.spines[['top','right']].set_visible(False)

# 2. MoM Growth bars
ax2 = axes[0,1]
mom_vals = sales['mom_pct'].iloc[1:]
months   = sales['month'].iloc[1:]
colors   = [GREEN if v >= 0 else CORAL for v in mom_vals]
ax2.bar(range(len(mom_vals)), mom_vals, color=colors, edgecolor='white')
ax2.axhline(0, color='gray', lw=0.8)
ax2.set_xticks(range(len(months))); ax2.set_xticklabels(months, rotation=40, ha='right', fontsize=8)
ax2.set_title('Month-over-Month Growth (%)', fontweight='bold')
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.grid(axis='y', alpha=0.3); ax2.spines[['top','right']].set_visible(False)

# 3. Cumulative revenue
ax3 = axes[1,0]
x = range(len(sales))
ax3.fill_between(x, sales['cumulative']/1000, alpha=0.18, color=NAVY)
ax3.plot(x, sales['cumulative']/1000, color=NAVY, lw=2.5, marker='o', markersize=5)
ax3.set_xticks(x); ax3.set_xticklabels(sales['month'], rotation=40, ha='right', fontsize=8)
ax3.set_title('Cumulative Revenue 2023 ($K)', fontweight='bold')
ax3.set_ylabel('Cumulative ($K)'); ax3.grid(axis='y', alpha=0.3)
ax3.spines[['top','right']].set_visible(False)

# 4. LTV by segment
ax4 = axes[1,1]
ltv_med = cust.groupby('segment')['ltv'].median().sort_values(ascending=False)
bar_colors = [NAVY,'#5B8DD9','#B0C4DE']
bars = ax4.bar(ltv_med.index, ltv_med.values, color=bar_colors, edgecolor='white', width=0.45)
for bar, v in zip(bars, ltv_med.values):
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+15,
             f'${v:,.0f}', ha='center', fontweight='bold', fontsize=12)
ax4.set_title('Median Customer LTV by Segment', fontweight='bold')
ax4.set_ylabel('Estimated LTV ($)'); ax4.grid(axis='y', alpha=0.3)
ax4.spines[['top','right']].set_visible(False)

plt.savefig('reports/figures/part2_deep_dive.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✅  reports/figures/part2_deep_dive.png")
