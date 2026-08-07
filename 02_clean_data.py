"""
Cleans the raw retail sales dataset:
1. Standardizes text fields (casing, whitespace)
2. Parses inconsistent date formats
3. Removes exact duplicate rows
4. Fixes impossible values (negative price/quantity)
5. Handles outliers (IQR capping)
6. Imputes missing values sensibly
7. Logs every step to a cleaning report
"""
import pandas as pd
import numpy as np

log = []

def note(msg):
    log.append(msg)
    print(msg)

df = pd.read_csv("/home/claude/raw_sales_data.csv")
note(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")

# --- 1. Standardize text columns ---
for col in ["Region", "Category", "Product", "PaymentMethod"]:
    df[col] = df[col].astype(str).str.strip().str.title()
    df.loc[df[col] == "Nan", col] = np.nan
note("Standardized text casing/whitespace in Region, Category, Product, PaymentMethod")

# --- 2. Parse mixed date formats ---
def parse_date(d):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y"):
        try:
            return pd.to_datetime(d, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["OrderDate"] = df["OrderDate"].apply(parse_date)
note(f"Parsed OrderDate into consistent datetime format ({df['OrderDate'].isna().sum()} unparseable)")

# --- 3. Remove exact duplicate rows (ignoring OrderID, since that's unique) ---
before = len(df)
dup_mask = df.drop(columns=["OrderID"]).duplicated(keep="first")
n_dupes = dup_mask.sum()
df = df[~dup_mask].reset_index(drop=True)
note(f"Removed {n_dupes} duplicate rows ({before} -> {len(df)})")

# --- 4. Fix impossible values ---
neg_qty = (df["Quantity"] < 0).sum()
df["Quantity"] = df["Quantity"].abs()
note(f"Corrected {neg_qty} negative Quantity values (converted to absolute value)")

neg_price = (df["UnitPrice"] < 0).sum()
df["UnitPrice"] = df["UnitPrice"].abs()
note(f"Corrected {neg_price} negative UnitPrice values (converted to absolute value)")

invalid_age = ((df["CustomerAge"] < 10) | (df["CustomerAge"] > 100)).sum()
df.loc[(df["CustomerAge"] < 10) | (df["CustomerAge"] > 100), "CustomerAge"] = np.nan
note(f"Flagged {invalid_age} impossible CustomerAge values (set to NaN for imputation)")

# --- 5. Outlier handling via IQR capping (winsorizing) ---
def cap_outliers(series, factor=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - factor * iqr, q3 + factor * iqr
    capped = series.clip(lower=lower, upper=upper)
    n_capped = (series != capped).sum()
    return capped, n_capped, lower, upper

df["UnitPrice"], n1, lo1, hi1 = cap_outliers(df["UnitPrice"])
note(f"Capped {n1} UnitPrice outliers to IQR bounds [{lo1:.2f}, {hi1:.2f}]")

df["Quantity"], n2, lo2, hi2 = cap_outliers(df["Quantity"])
note(f"Capped {n2} Quantity outliers to IQR bounds [{lo2:.2f}, {hi2:.2f}]")

# --- 6. Impute missing values ---
missing_before = df.isna().sum()

# Numeric -> median (robust to remaining skew), grouped by Category where sensible
df["UnitPrice"] = df.groupby("Category")["UnitPrice"].transform(lambda s: s.fillna(s.median()))
df["CustomerAge"] = df["CustomerAge"].fillna(df["CustomerAge"].median())
df["Rating"] = df["Rating"].fillna(df["Rating"].median())

# Categorical -> mode
df["Region"] = df["Region"].fillna(df["Region"].mode()[0])
df["PaymentMethod"] = df["PaymentMethod"].fillna(df["PaymentMethod"].mode()[0])

missing_after = df.isna().sum()
note("Imputed missing values: numeric columns with (grouped) median, categorical with mode")
for col in df.columns:
    if missing_before[col] > 0:
        note(f"   - {col}: {missing_before[col]} missing -> {missing_after[col]} missing")

# Drop any remaining rows with missing critical fields (e.g. unparseable dates)
before_drop = len(df)
df = df.dropna(subset=["OrderDate", "OrderID"])
note(f"Dropped {before_drop - len(df)} rows with missing critical fields (OrderID/OrderDate)")

# --- 7. Add derived column for analysis ---
df["Revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)
df["Month"] = df["OrderDate"].dt.to_period("M").astype(str)
note("Added derived columns: Revenue (Quantity x UnitPrice), Month")

# --- Save cleaned data ---
df.to_csv("/home/claude/cleaned_sales_data.csv", index=False)
note(f"\nFinal cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
note(f"Remaining nulls: {int(df.isna().sum().sum())}")

with open("/home/claude/cleaning_report.md", "w") as f:
    f.write("# Data Cleaning Report\n\n")
    f.write(f"**Raw rows:** {before}  \n**Cleaned rows:** {len(df)}  \n\n")
    f.write("## Steps Performed\n\n")
    for i, entry in enumerate(log, 1):
        f.write(f"{i}. {entry}\n")

print("\nCleaning complete. Report saved to cleaning_report.md")
