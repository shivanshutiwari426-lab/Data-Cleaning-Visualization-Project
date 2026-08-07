"""
Builds a visual dashboard of key insights from the cleaned sales data.
Outputs a single high-res PNG dashboard plus individual chart files.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

df = pd.read_csv("/home/claude/cleaned_sales_data.csv", parse_dates=["OrderDate"])

sns.set_theme(style="whitegrid", font_scale=0.95)
palette = sns.color_palette("mako", 8)

fig = plt.figure(figsize=(18, 12))
fig.suptitle("Retail Sales — Data Insights Dashboard", fontsize=20, fontweight="bold", y=0.99)
gs = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.35)

# 1. Revenue trend over time (monthly)
ax1 = fig.add_subplot(gs[0, :2])
monthly = df.groupby("Month")["Revenue"].sum().reset_index().sort_values("Month")
ax1.plot(monthly["Month"], monthly["Revenue"], marker="o", color=palette[4], linewidth=2)
ax1.set_title("Monthly Revenue Trend", fontweight="bold")
ax1.set_ylabel("Revenue ($)")
ax1.tick_params(axis="x", rotation=45)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))

# 2. Revenue by category
ax2 = fig.add_subplot(gs[0, 2])
cat_rev = df.groupby("Category")["Revenue"].sum().sort_values(ascending=True)
ax2.barh(cat_rev.index, cat_rev.values, color=palette[3])
ax2.set_title("Revenue by Category", fontweight="bold")
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))

# 3. Revenue by region
ax3 = fig.add_subplot(gs[1, 0])
reg_rev = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
ax3.bar(reg_rev.index, reg_rev.values, color=palette[2])
ax3.set_title("Revenue by Region", fontweight="bold")
ax3.tick_params(axis="x", rotation=30)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))

# 4. Payment method distribution
ax4 = fig.add_subplot(gs[1, 1])
pay_counts = df["PaymentMethod"].value_counts()
ax4.pie(pay_counts.values, labels=pay_counts.index, autopct="%1.0f%%",
        colors=sns.color_palette("mako", len(pay_counts)), startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1})
ax4.set_title("Payment Method Share", fontweight="bold")

# 5. Rating distribution
ax5 = fig.add_subplot(gs[1, 2])
sns.histplot(df["Rating"], bins=15, color=palette[5], ax=ax5, kde=True)
ax5.set_title("Customer Rating Distribution", fontweight="bold")
ax5.set_xlabel("Rating")

# 6. UnitPrice distribution (post-cleaning, showing capped outliers)
ax6 = fig.add_subplot(gs[2, 0])
sns.boxplot(y=df["UnitPrice"], color=palette[1], ax=ax6)
ax6.set_title("Unit Price Spread (Post-Cleaning)", fontweight="bold")

# 7. Age vs Rating scatter
ax7 = fig.add_subplot(gs[2, 1])
sns.scatterplot(data=df.sample(min(500, len(df)), random_state=1),
                 x="CustomerAge", y="Rating", hue="Category", ax=ax7,
                 palette="mako", legend=False, alpha=0.6, s=25)
ax7.set_title("Customer Age vs Rating (sample)", fontweight="bold")

# 8. Top products by revenue
ax8 = fig.add_subplot(gs[2, 2])
top_products = df.groupby("Product")["Revenue"].sum().sort_values(ascending=True).tail(8)
ax8.barh(top_products.index, top_products.values, color=palette[6])
ax8.set_title("Top Products by Revenue", fontweight="bold")
ax8.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))

plt.savefig("/home/claude/sales_dashboard.png", dpi=150, bbox_inches="tight", facecolor="white")
print("Dashboard saved.")

# --- Individual key chart for closer inspection: revenue trend ---
plt.figure(figsize=(10, 5))
plt.plot(monthly["Month"], monthly["Revenue"], marker="o", color=palette[4])
plt.title("Monthly Revenue Trend", fontsize=14, fontweight="bold")
plt.xticks(rotation=45)
plt.ylabel("Revenue ($)")
plt.tight_layout()
plt.savefig("/home/claude/monthly_revenue_trend.png", dpi=150, facecolor="white")
print("Saved individual chart: monthly_revenue_trend.png")

# --- Summary stats for report ---
summary = {
    "total_revenue": df["Revenue"].sum(),
    "total_orders": len(df),
    "avg_order_value": df["Revenue"].mean(),
    "avg_rating": df["Rating"].mean(),
    "top_category": cat_rev.idxmax(),
    "top_region": reg_rev.idxmax(),
}
import json
with open("/home/claude/summary_stats.json", "w") as f:
    json.dump({k: (round(v, 2) if isinstance(v, float) else v) for k, v in summary.items()}, f, indent=2)
print(summary)
