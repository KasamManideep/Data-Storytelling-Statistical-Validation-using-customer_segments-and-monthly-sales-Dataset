import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import stats
import sys
sys.stdout.reconfigure(encoding='utf-8')

ab   = pd.read_csv('data/ab_test_results.csv')
cust = pd.read_csv('data/customer_segments.csv')

NAVY, GREEN, CORAL = '#1E2761', '#2d7a2d', '#F96167'
results = {}

def sig(p): return "✓ SIGNIFICANT (p<0.05)" if p < 0.05 else "✗ NOT SIGNIFICANT"

print("="*65)
print("PART 3 — HYPOTHESIS TESTING REPORT")
print("="*65)

# ══════════════════════════════════════════════════════
# TEST 1 — Chi-Squared: Conversion Rate A/B
# ══════════════════════════════════════════════════════
ctrl  = ab[ab['group']=='Control']
treat = ab[ab['group']=='Treatment']
c_conv, c_n = ctrl['converted'].sum(), len(ctrl)
t_conv, t_n = treat['converted'].sum(), len(treat)
cr, tr = c_conv/c_n, t_conv/t_n
lift_pct = (tr/cr - 1)*100

table = np.array([[c_conv, c_n-c_conv],
                  [t_conv, t_n-t_conv]])
chi2, p1, dof, _ = stats.chi2_contingency(table)

print(f"""
┌──────────────────────────────────────────────────────────┐
│  TEST 1 · Chi-Squared  — Conversion Rate Difference      │
└──────────────────────────────────────────────────────────┘
  H0: p_control = p_treatment
  H1: p_treatment > p_control

  Control   : {c_conv}/{c_n} conversions = {cr:.2%}
  Treatment : {t_conv}/{t_n} conversions = {tr:.2%}
  Lift      : {lift_pct:+.1f}%

  χ² = {chi2:.4f}   p-value = {p1:.4f}   df = {dof}

  → {sig(p1)}
""")
results['test1'] = dict(test='Chi-Squared', chi2=round(chi2,4), p=round(p1,4),
                        ctrl_rate=round(cr,4), treat_rate=round(tr,4),
                        lift_pct=round(lift_pct,2), significant=bool(p1<0.05))

# ══════════════════════════════════════════════════════
# TEST 2 — T-Test: Revenue per User
# ══════════════════════════════════════════════════════
cr_rev = ctrl['revenue_usd']
tr_rev = treat['revenue_usd']
t_stat, p2 = stats.ttest_ind(tr_rev, cr_rev, alternative='greater')
diff = tr_rev.mean() - cr_rev.mean()
se   = np.sqrt(cr_rev.var()/len(cr_rev) + tr_rev.var()/len(tr_rev))
ci_lo, ci_hi = diff - 1.96*se, diff + 1.96*se

print(f"""┌──────────────────────────────────────────────────────────┐
│  TEST 2 · Two-Sample T-Test  — Revenue per User           │
└──────────────────────────────────────────────────────────┘
  H0: μ_control = μ_treatment
  H1: μ_treatment > μ_control

  Control avg   : ${cr_rev.mean():.2f}  (SD ${cr_rev.std():.2f})
  Treatment avg : ${tr_rev.mean():.2f}  (SD ${tr_rev.std():.2f})

  t = {t_stat:.4f}   p-value = {p2:.4f}
  95% CI for Δ  : (${ci_lo:.2f},  ${ci_hi:.2f})

  → {sig(p2)}
""")
results['test2'] = dict(test='T-Test', t_stat=round(t_stat,4), p=round(p2,4),
                        ci_lo=round(ci_lo,2), ci_hi=round(ci_hi,2), significant=bool(p2<0.05))

# ══════════════════════════════════════════════════════
# TEST 3 — One-Way ANOVA: Spend by Segment
# ══════════════════════════════════════════════════════
prem = cust[cust['segment']=='Premium']['annual_spend']
std  = cust[cust['segment']=='Standard']['annual_spend']
bud  = cust[cust['segment']=='Budget']['annual_spend']
F, p3 = stats.f_oneway(prem, std, bud)

print(f"""┌──────────────────────────────────────────────────────────┐
│  TEST 3 · One-Way ANOVA  — Spend Across Segments          │
└──────────────────────────────────────────────────────────┘
  H0: μ_premium = μ_standard = μ_budget
  H1: At least one segment mean differs

  Premium  : mean=${prem.mean():.2f}  n={len(prem)}
  Standard : mean=${std.mean():.2f}  n={len(std)}
  Budget   : mean=${bud.mean():.2f}  n={len(bud)}

  F = {F:.4f}   p-value = {p3:.6f}

  → {sig(p3)}
""")
results['test3'] = dict(test='ANOVA', F=round(F,4), p=round(p3,8), significant=bool(p3<0.05))

# Save JSON
with open('reports/hypothesis_summary.json', 'w') as f:
    json.dump(results, f, indent=2)

# ── Figure ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Part 3 — Hypothesis Testing Results', fontsize=15, fontweight='bold')
plt.subplots_adjust(wspace=0.35)

# 1. Conversion rates
ax1 = axes[0]
bars = ax1.bar(['Control','Treatment'], [cr*100, tr*100], color=[CORAL, GREEN],
               edgecolor='white', width=0.45)
for bar, v in zip(bars, [cr*100, tr*100]):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
             f'{v:.1f}%', ha='center', fontweight='bold', fontsize=13)
ax1.set_title(f'Test 1 · χ²-test\np={p1:.4f}  {"✓" if p1<0.05 else "✗"}', fontweight='bold')
ax1.set_ylabel('Conversion Rate (%)'); ax1.set_ylim(0, max(cr,tr)*140)
ax1.grid(axis='y', alpha=0.3); ax1.spines[['top','right']].set_visible(False)

# 2. Revenue histogram
ax2 = axes[1]
ax2.hist(cr_rev[cr_rev>0], bins=22, alpha=0.55, color=CORAL, label='Control', edgecolor='white')
ax2.hist(tr_rev[tr_rev>0], bins=22, alpha=0.55, color=GREEN, label='Treatment', edgecolor='white')
ax2.axvline(cr_rev.mean(), color='darkred', lw=2, ls='--', label=f'C̄={cr_rev.mean():.0f}')
ax2.axvline(tr_rev.mean(), color='darkgreen', lw=2, ls='--', label=f'T̄={tr_rev.mean():.0f}')
ax2.set_title(f'Test 2 · T-test\np={p2:.4f}  {"✓" if p2<0.05 else "✗"}', fontweight='bold')
ax2.set_xlabel('Revenue ($)'); ax2.set_ylabel('Users')
ax2.legend(fontsize=9); ax2.grid(axis='y', alpha=0.3); ax2.spines[['top','right']].set_visible(False)

# 3. Segment boxplot
ax3 = axes[2]
bp = ax3.boxplot([prem, std, bud], labels=['Premium','Standard','Budget'],
                 patch_artist=True, medianprops=dict(color='white', linewidth=2))
for patch, col in zip(bp['boxes'], [NAVY,'#5B8DD9','#B0C4DE']):
    patch.set_facecolor(col); patch.set_alpha(0.8)
ax3.set_title(f'Test 3 · ANOVA\np={p3:.4f}  {"✓" if p3<0.05 else "✗"}', fontweight='bold')
ax3.set_ylabel('Annual Spend ($)'); ax3.grid(axis='y', alpha=0.3)
ax3.spines[['top','right']].set_visible(False)

plt.savefig('reports/figures/part3_hypothesis.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅  reports/figures/part3_hypothesis.png")
print("✅  reports/hypothesis_summary.json")
