# Data Cleaning Report

**Raw rows:** 2040  
**Cleaned rows:** 2000  

## Steps Performed

1. Loaded raw data: 2040 rows, 10 columns
2. Standardized text casing/whitespace in Region, Category, Product, PaymentMethod
3. Parsed OrderDate into consistent datetime format (0 unparseable)
4. Removed 40 duplicate rows (2040 -> 2000)
5. Corrected 6 negative Quantity values (converted to absolute value)
6. Corrected 4 negative UnitPrice values (converted to absolute value)
7. Flagged 5 impossible CustomerAge values (set to NaN for imputation)
8. Capped 129 UnitPrice outliers to IQR bounds [-40.71, 424.65]
9. Capped 10 Quantity outliers to IQR bounds [-6.50, 21.50]
10. Imputed missing values: numeric columns with (grouped) median, categorical with mode
11.    - Region: 40 missing -> 0 missing
12.    - UnitPrice: 80 missing -> 0 missing
13.    - CustomerAge: 125 missing -> 0 missing
14.    - PaymentMethod: 60 missing -> 0 missing
15.    - Rating: 160 missing -> 0 missing
16. Dropped 0 rows with missing critical fields (OrderID/OrderDate)
17. Added derived columns: Revenue (Quantity x UnitPrice), Month
18. 
Final cleaned dataset: 2000 rows, 12 columns
19. Remaining nulls: 0
