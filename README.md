# Superstore Sales Case Study

This project presents an end-to-end Exploratory Data Analysis (EDA) of a retail dataset (Superstore), focusing on data cleaning, enrichment, and business insights generation. The aim is to build a clean, enriched dataset for strategic decision-making and visual storytelling.

---

##  Dataset

- **Source**: Superstore retail sales
- **Records**: 9994+
- **Columns**: 21 including Order details, Product, Customer, and Financials

---

##  Step-by-Step Approach

### 1. Data Overview

Initial inspection includes:

- Data shape, types, missing values
- Summary statistics and uniqueness analysis

**Plot:**  
![Missing Values Heatmap](./plots/01_missing_values_heatmap.png)

---

### 2. Duplicate Records Handling

- Identified duplicate Order IDs
- Removed 999+ duplicate rows
- Preserved data quality for analysis

**Plot:**  
![Top 10 Duplicate Order IDs](plots/02_top_duplicates.png)

---

### 3. Date Fixing from Order ID

- Order ID contains embedded year (e.g. `CA-2014-XXXX`)
- Ensured `Order Date` year matched embedded year
- Fixed mismatches by replacing year in `Order Date`

**Plots:**

- ![Year Match Count](plots/03_order_year_match.png)
- ![Monthly Order Volume](plots/04_monthly_orders.png)

---

### 4. Shipping Time & Quantity Cleanup

- Computed `Days to Ship` from `Order Date` and `Ship Date`
- Imputed missing Ship Mode where possible
- Cleaned quantity column using median imputation

**Plots:**

- ![Quantity Box Plot](plots/06_quantity_boxplot.png)
- ![Days to Ship Histogram](plots/05_days_to_ship.png)

---

### 5. Customer Privacy Masking

- Converted full names to initials (e.g. "John Doe"  "J.D.")
- Dropped original names for privacy

**Plot:**

- ![Top 20 Customer Initials](plots/07_customer_initials.png)

---

### 6. Postal Code & Type Conversion

- Standardized `Postal Code` to 5-digit format
- Converted `Sales Price` and `Profit` to numeric

---

### 7. State Mapping

- Replaced state abbreviations (e.g. "CA") with full names using US reference file

**Plot:**

- ![Top States by Orders](plots/08_top_states.png)

---

### 8. Feature Engineering

- Derived:
  - `Original Price` (before discount)
  - `Total Sales`, `Total Profit`, `Discount Price`, `Total Discount`
  - `Shipping Urgency` buckets: Immediate, Urgent, Standard

**Plot:**

- ![Shipping Urgency Count](plots/09_shipping_urgency.png)

---

### 9. Outlier Removal (3IQR)

- Removed outliers from:
  - `Sales Price`
  - `Profit`

**Plots:**

- ![Original Price Histogram](plots/10_original_price.png)
- ![Discount Price Histogram](plots/11_discount_price.png)
- ![Total Discount Histogram](plots/12_total_discount.png)

---

### 10. Customer Segmentation (RFM-inspired)

- Calculated quintiles for:
  - `Total Sales`
  - `Total Profit`

- Created segmentation heatmap

**Plots:**

- ![Sales Price Box Plot](plots/10_sales_price_boxplot.png)
- ![Profit Box Plot](plots/10_profit_boxplot.png)
- ![Sales vs Profit Segmentation](plots/10_quintile_heatmap.png)

---

### 11. Profitability Analysis

- Identified:
  - Top 10 profitable products
  - Top 10 loss-making products

**Plots:**

- ![Top Profitable Products](plots/11_top_profit_products.png)
- ![Top Loss Products](plots/11_loss_products.png)
---

##  Output

- Cleaned dataset: `SuperStore_Cleaned_Final.csv`

---

##  Why This Approach

- **Data Validation**: Ensures data trust before insights
- **Customer Privacy**: Important for ethical analysis
- **Feature Engineering**: Adds business depth
- **Outlier Removal**: Improves segmentation robustness
- **Segmentation**: Enables actionable points for marketing

---

##  Folder Structure

```
Superstore_Case_Study/
 SuperStore_Dataset.csv
 SuperStore_Cleaned_Final.csv
 Superstore-Sales-Case-Study.ipynb
 app.py
 README.md
 plots/
     01_missing_values.png
     02_top_duplicates.png
     ...
```

---

##  Tech Stack

- Python 3.12
- Pandas 2.3.1
- Seaborn, Matplotlib
- Jupyter Notebook