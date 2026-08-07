"""
Generates a realistic, messy raw retail sales dataset to simulate
real-world data quality issues:
- Missing values (NaNs) scattered across several columns
- Duplicate rows
- Outliers in price/quantity
- Inconsistent text casing / whitespace
- Inconsistent date formats
- A few impossible values (negative quantity, negative price)
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N = 2000

regions = ["North", "South", "East", "West", "Central"]
categories = ["Electronics", "Clothing", "Home & Kitchen", "Sports", "Books", "Toys"]
payment_methods = ["Credit Card", "Debit Card", "UPI", "Cash", "Net Banking"]

start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=int(x)) for x in np.random.randint(0, 545, N)]

df = pd.DataFrame({
    "OrderID": [f"ORD{1000+i}" for i in range(N)],
    "OrderDate": dates,
    "Region": np.random.choice(regions, N),
    "Category": np.random.choice(categories, N),
    "Product": np.random.choice(
        ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Gizmo Z",
         "Device Q", "Accessory M", "Item N"], N),
    "Quantity": np.random.randint(1, 15, N),
    "UnitPrice": np.round(np.random.gamma(5, 40, N), 2),
    "CustomerAge": np.random.randint(18, 70, N),
    "PaymentMethod": np.random.choice(payment_methods, N),
    "Rating": np.round(np.random.uniform(1, 5, N), 1),
})

# ---- Inject messiness ----

# 1. Missing values
for col, frac in [("UnitPrice", 0.04), ("CustomerAge", 0.06),
                   ("Rating", 0.08), ("Region", 0.02), ("PaymentMethod", 0.03)]:
    idx = np.random.choice(df.index, int(N * frac), replace=False)
    df.loc[idx, col] = np.nan

# 2. Outliers
outlier_idx = np.random.choice(df.index, 15, replace=False)
df.loc[outlier_idx, "UnitPrice"] = df.loc[outlier_idx, "UnitPrice"] * np.random.uniform(15, 40, 15)

outlier_idx2 = np.random.choice(df.index, 10, replace=False)
df.loc[outlier_idx2, "Quantity"] = np.random.randint(200, 500, 10)

age_outlier_idx = np.random.choice(df.index, 5, replace=False)
df.loc[age_outlier_idx, "CustomerAge"] = np.random.choice([120, 150, 200, -5, 300], 5)

# 3. Impossible / invalid values
neg_idx = np.random.choice(df.index, 6, replace=False)
df.loc[neg_idx, "Quantity"] = -df.loc[neg_idx, "Quantity"]

neg_price_idx = np.random.choice(df.index, 4, replace=False)
df.loc[neg_price_idx, "UnitPrice"] = -df.loc[neg_price_idx, "UnitPrice"]

# 4. Inconsistent text casing / whitespace
def messy_case(x):
    r = np.random.random()
    if r < 0.2:
        return x.upper()
    elif r < 0.4:
        return x.lower()
    elif r < 0.5:
        return f"  {x}  "
    return x

df["Region"] = df["Region"].apply(lambda x: messy_case(x) if pd.notna(x) else x)
df["Category"] = df["Category"].apply(lambda x: messy_case(x) if pd.notna(x) else x)

# 5. Inconsistent date formats (mix strings)
def messy_date(d):
    r = np.random.random()
    if r < 0.3:
        return d.strftime("%Y-%m-%d")
    elif r < 0.6:
        return d.strftime("%d/%m/%Y")
    elif r < 0.8:
        return d.strftime("%m-%d-%Y")
    return d.strftime("%d %b %Y")

df["OrderDate"] = df["OrderDate"].apply(messy_date)

# 6. Duplicates - append exact copies of random rows
dupes = df.sample(40, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# shuffle
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("/home/claude/raw_sales_data.csv", index=False)
print("Raw dataset created:", df.shape)
print(df.head())
