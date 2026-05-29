import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
sys.stdout.reconfigure(encoding='utf-8')

ab    = pd.read_csv('data/ab_test_results.csv')
sales = pd.read_csv('data/monthly_sales.csv')
cust  = pd.read_csv('data/customer_segments.csv')

print("="*60)
print("PART 1 — EXPLORATORY DATA ANALYSIS")
print("="*60)

print("\n── A/B TEST ──────────────────────────────────────────────")
grp = ab.groupby('group').agg(
    Users=('user_id','count'),
    Conversions=('converted','sum'),
    Conv_Rate=('converted','mean'),
    Avg_Revenue=('revenue_usd','mean')
).round(4)
print(grp)

print("\n── MONTHLY SALES ─────────────────────────────────────────")
total = sales['monthly_revenue'].sum()
avg   = sales['monthly_revenue'].mean()
growth= (sales['monthly_revenue'].iloc[-1]/sales['monthly_revenue'].iloc[0]-1)*100
print(f"  Total Revenue : ${total:,.0f}")
print(f"  Monthly Avg   : ${avg:,.0f}")
print(f"  Jan→Dec Growth: {growth:.1f}%")

print("\n── CUSTOMER SEGMENTS ─────────────────────────────────────")
seg = cust.groupby('segment')['annual_spend'].agg(['count','mean','sum']).round(2)
seg.columns = ['Count','Avg Spend','Total Spend']
print(seg)

# ── Figure ───────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8))
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)
fig.suptitle('Part 1 — Exploratory Data Analysis', fontsize=16, fontweight='bold')

NAVY, GREEN, CORAL = '#1E2761', '#2d7a2d', '#F96167'

# 1. Sales trend
ax1 = fig.add_subplot(gs[0, 0])
x = range(len(sales))
ax1.fill_between(x, sales['monthly_revenue'], alpha=0.18, color=NAVY)
ax1.plot(x, sales['monthly_revenue'], color=NAVY, linewidth=2.5, marker='o', markersize=5)
ax1.set_title('Monthly Revenue Trend (2023)', fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(sales['month'], rotation=40, ha='right', fontsize=8)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'${v/1000:.0f}K'))
ax1.grid(axis='y', alpha=0.3); ax1.spines[['top','right']].set_visible(False)

# 2. A/B conversion rates
ax2 = fig.add_subplot(gs[0, 1])
rates = ab.groupby('group')['converted'].mean() * 100
bars  = ax2.bar(rates.index, rates.values, color=[CORAL, GREEN], edgecolor='white', width=0.45)
for bar, v in zip(bars, rates.values):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.25,
             f'{v:.1f}%', ha='center', fontweight='bold', fontsize=13)
ax2.set_title('A/B Test: Conversion Rate', fontweight='bold')
ax2.set_ylabel('Conversion Rate (%)'); ax2.set_ylim(0, max(rates.values)*1.4)
ax2.grid(axis='y', alpha=0.3); ax2.spines[['top','right']].set_visible(False)

# 3. Customer segment pie
ax3 = fig.add_subplot(gs[1, 0])
seg_cnt = cust['segment'].value_counts()
ax3.pie(seg_cnt, labels=seg_cnt.index, autopct='%1.1f%%',
        colors=['#1E2761','#5B8DD9','#B0C4DE'], startangle=90,
        wedgeprops=dict(edgecolor='white', linewidth=2))
ax3.set_title('Customer Segment Mix', fontweight='bold')

# 4. Spend distribution
ax4 = fig.add_subplot(gs[1, 1])
palette = {'Premium':'#1E2761', 'Standard':'#5B8DD9', 'Budget':'#B0C4DE'}
for seg, col in palette.items():
    data = cust[cust['segment']==seg]['annual_spend']
    ax4.hist(data, bins=20, alpha=0.65, color=col, label=seg, edgecolor='white')
ax4.set_title('Annual Spend by Segment', fontweight='bold')
ax4.set_xlabel('Annual Spend ($)'); ax4.set_ylabel('Count')
ax4.legend(); ax4.grid(axis='y', alpha=0.3); ax4.spines[['top','right']].set_visible(False)

plt.savefig('reports/figures/part1_eda.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✅  reports/figures/part1_eda.png")
