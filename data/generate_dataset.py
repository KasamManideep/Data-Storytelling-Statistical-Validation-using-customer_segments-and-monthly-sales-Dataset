import pandas as pd
import numpy as np

np.random.seed(42)

#1. A/B TEST DATA (website layout experiment) 
n = 600
group  = np.random.choice(['Control', 'Treatment'], n, p=[0.5, 0.5])
device = np.random.choice(['Mobile', 'Desktop', 'Tablet'], n, p=[0.55, 0.35, 0.10])
region = np.random.choice(['North', 'South', 'East', 'West'], n)

conv_rate = np.where(group == 'Treatment', 0.18, 0.12)
converted = np.array([np.random.binomial(1, r) for r in conv_rate])
revenue   = np.where(converted == 1,
                     np.random.normal(90, 22, n).clip(20, 250),
                     0.0).round(2)

ab_df = pd.DataFrame({
    'user_id':              range(1, n+1),
    'group':                group,
    'device':               device,
    'region':               region,
    'converted':            converted,
    'revenue_usd':          revenue,
    'session_duration_sec': np.random.normal(185, 65, n).clip(15).round(0).astype(int),
    'pages_visited':        np.random.poisson(4.2, n).clip(1),
})

ab_df.to_csv('data/ab_test_results.csv', index=False)
print(f"ab_test_results.csv ({len(ab_df)} rows)")

#2. MONTHLY SALES DATA 
months = pd.date_range('2023-01-01', periods=12, freq='MS').strftime('%b %Y')
sales  = [41000, 37500, 50000, 54000, 61000, 68000,
          73500, 71000, 66000, 79000, 87000, 96500]
mkt    = [6500, 5800, 7200, 8100, 9000, 10500,
          11000, 10200, 9500, 12000, 14000, 15500]

sales_df = pd.DataFrame({
    'month':             months,
    'monthly_revenue':   sales,
    'units_sold':        [int(s / 118) for s in sales],
    'new_customers':     np.random.randint(85, 210, 12).tolist(),
    'returning_customers': np.random.randint(160, 420, 12).tolist(),
    'marketing_spend':   mkt,
    'return_on_ad_spend': [round(s / m, 2) for s, m in zip(sales, mkt)],
})

sales_df.to_csv('data/monthly_sales.csv', index=False)
print(f"monthly_sales.csv ({len(sales_df)} rows)")
#3. CUSTOMER SEGMENTS 
nc = 400
segments = np.random.choice(['Premium', 'Standard', 'Budget'],
                             nc, p=[0.20, 0.50, 0.30])
spend_mu = {'Premium': 820, 'Standard': 380, 'Budget': 140}
spend = np.array([np.random.normal(spend_mu[s], spend_mu[s]*0.25) for s in segments]).clip(30).round(2)

cust_df = pd.DataFrame({
    'customer_id':    range(1, nc+1),
    'segment':        segments,
    'age':            np.random.normal(38, 11, nc).clip(18, 72).round(0).astype(int),
    'annual_spend':   spend,
    'loyalty_years':  np.random.randint(0, 12, nc),
    'nps_score':      np.random.randint(1, 11, nc),
    'churn_risk':     np.random.choice(['Low', 'Medium', 'High'], nc, p=[0.5, 0.3, 0.2]),
})

cust_df.to_csv('data/customer_segments.csv', index=False)
print(f"customer_segments.csv ({len(cust_df)} rows)")

print("\nAll datasets saved in  data/")
