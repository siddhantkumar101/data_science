import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Set modern visual aesthetics for matplotlib/seaborn
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'figure.figsize': (10, 6),
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'image.cmap': 'viridis'
})

# Define Custom harmonized color palette (cool tech look)
PALETTE = ["#4A90E2", "#50E3C2", "#F5A623", "#9B51E0", "#E2849A"]
sns.set_palette(PALETTE)

def clean_data(raw_path, clean_path):
    print("=" * 60)
    print(" STAGE 1: DATA CLEANING & PREPROCESSING")
    print("=" * 60)
    
    # 1. Load data
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_path}")
    
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    print(f"Loaded raw dataset with {initial_rows} records.")
    
    # 2. Drop duplicates
    duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates()
    print(f"-> Detected and removed {duplicates_count} exact duplicate records.")
    
    # 3. Clean Text Fields (strip whitespaces, standardize capitalization)
    df['Category'] = df['Category'].fillna('Unknown')
    df['Category'] = df['Category'].str.strip().str.title()
    
    # Standardize category names
    df['Category'] = df['Category'].replace({'Accessories': 'Accessories'}) # Handle case variations
    
    df['Region'] = df['Region'].fillna('Unknown')
    df['Region'] = df['Region'].str.strip().str.title()
    df['Region'] = df['Region'].replace({'South': 'South', 'North': 'North', 'East': 'East', 'West': 'West'})
    
    df['Customer_Segment'] = df['Customer_Segment'].fillna('Consumer').str.strip().str.title()
    df['Payment_Method'] = df['Payment_Method'].fillna('Unknown').str.strip()
    df['Product_Name'] = df['Product_Name'].fillna('Unknown').str.strip()
    
    # 4. Inconsistent Date Format Cleaning
    def parse_date(x):
        if pd.isna(x):
            return pd.NaT
        x = str(x).strip()
        for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
            try:
                return pd.to_datetime(x, format=fmt)
            except (ValueError, TypeError):
                continue
        return pd.to_datetime(x, errors='coerce')

    df['Parsed_Date'] = df['Date'].apply(parse_date)
    missing_dates = df['Parsed_Date'].isna().sum()
    if missing_dates > 0:
        print(f"-> Warning: Could not parse {missing_dates} dates. Dropping these rows.")
        df = df.dropna(subset=['Parsed_Date'])
        
    df['Date'] = df['Parsed_Date'].dt.strftime('%Y-%m-%d')
    
    # 5. Handle missing values in critical columns
    # Customer_ID
    missing_cust = df['Customer_ID'].isna().sum()
    df['Customer_ID'] = df['Customer_ID'].fillna('CUST-UNKNOWN')
    
    # Region 'Unknown' imputation (fill with mode)
    mode_region = df[df['Region'] != 'Unknown']['Region'].mode()[0]
    df['Region'] = df['Region'].replace('Unknown', mode_region)
    
    # Quantity
    missing_qty = df['Quantity'].isna().sum()
    median_qty = df['Quantity'].median()
    # If median is nan, default to 1.0
    if pd.isna(median_qty):
        median_qty = 1.0
    df['Quantity'] = df['Quantity'].fillna(median_qty)
    
    # Unit_Price
    missing_price = df['Unit_Price'].isna().sum()
    # Impute missing price with median price for that specific product
    product_price_medians = df.groupby('Product_Name')['Unit_Price'].median().to_dict()
    def impute_price(row):
        if pd.isna(row['Unit_Price']) or row['Unit_Price'] == 0.0:
            return product_price_medians.get(row['Product_Name'], 29.99)
        return row['Unit_Price']
    
    df['Unit_Price'] = df.apply(impute_price, axis=1)
    print(f"-> Imputed {missing_cust} missing Customer IDs, {missing_qty} missing Quantities, and {missing_price} missing/zero Unit Prices.")
    
    # 6. Handle Outliers and Typos
    # Quantity outliers: negative values replaced with median; huge values (> 100) replaced with median
    neg_qty = (df['Quantity'] < 0).sum()
    huge_qty = (df['Quantity'] > 100).sum()
    
    df.loc[df['Quantity'] < 0, 'Quantity'] = median_qty
    df.loc[df['Quantity'] > 100, 'Quantity'] = median_qty
    print(f"-> Corrected Quantity anomalies: {neg_qty} negative values and {huge_qty} extreme (>100) values reset to median ({median_qty}).")
    
    # Unit Price Outliers: typo prices (e.g. 9999.99) replaced with product median
    huge_prices = (df['Unit_Price'] > 2000.0).sum()
    def correct_huge_price(row):
        if row['Unit_Price'] > 2000.0:
            return product_price_medians.get(row['Product_Name'], 29.99)
        return row['Unit_Price']
    df['Unit_Price'] = df.apply(correct_huge_price, axis=1)
    print(f"-> Corrected {huge_prices} extreme Unit Price outliers (> $2000.0) reset to product-specific medians.")
    
    # 7. Compute Total Revenue
    df['Quantity'] = df['Quantity'].astype(int)
    df['Unit_Price'] = df['Unit_Price'].astype(float)
    df['Total_Revenue'] = df['Quantity'] * df['Unit_Price']
    
    # Drop temp column and save
    df = df.drop(columns=['Parsed_Date'])
    
    # Make sure clean folder exists and save
    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    df.to_csv(clean_path, index=False)
    
    final_rows = len(df)
    print(f"Data cleaning complete! Saved cleaned dataset to {clean_path}")
    print(f"Final record count: {final_rows} (dropped {initial_rows - final_rows} invalid/duplicate rows)")
    print("-" * 60)
    return df

def perform_eda(df):
    print("=" * 60)
    print(" STAGE 2: EXPLORATORY DATA ANALYSIS (EDA) & STATS")
    print("=" * 60)
    
    total_rev = df['Total_Revenue'].sum()
    avg_order = df['Total_Revenue'].mean()
    total_tx = len(df)
    unique_cust = df['Customer_ID'].nunique()
    total_qty = df['Quantity'].sum()
    
    print("--- KEY PERFORMANCE INDICATORS (KPIs) ---")
    print(f"Total Revenue:              ${total_rev:,.2f}")
    print(f"Total Transactions:         {total_tx:,}")
    print(f"Average Order Value (AOV):  ${avg_order:.2f}")
    print(f"Total Units Sold:           {total_qty:,}")
    print(f"Unique Customers:           {unique_cust}")
    print("-" * 40)
    
    print("\n--- REVENUE BY PRODUCT CATEGORY ---")
    cat_summary = df.groupby('Category').agg(
        Revenue=('Total_Revenue', 'sum'),
        Units_Sold=('Quantity', 'sum'),
        Transactions=('Transaction_ID', 'count')
    ).sort_values(by='Revenue', ascending=False)
    cat_summary['Revenue_Share_%'] = (cat_summary['Revenue'] / total_rev) * 100
    print(cat_summary.to_string(formatters={
        'Revenue': '${:,.2f}'.format,
        'Units_Sold': '{:,}'.format,
        'Transactions': '{:,}'.format,
        'Revenue_Share_%': '{:.1f}%'.format
    }))
    
    print("\n--- REVENUE BY REGION ---")
    reg_summary = df.groupby('Region').agg(
        Revenue=('Total_Revenue', 'sum'),
        Transactions=('Transaction_ID', 'count'),
        AOV=('Total_Revenue', 'mean')
    ).sort_values(by='Revenue', ascending=False)
    print(reg_summary.to_string(formatters={
        'Revenue': '${:,.2f}'.format,
        'Transactions': '{:,}'.format,
        'AOV': '${:,.2f}'.format
    }))
    
    print("\n--- REVENUE BY CUSTOMER SEGMENT ---")
    seg_summary = df.groupby('Customer_Segment').agg(
        Revenue=('Total_Revenue', 'sum'),
        Transactions=('Transaction_ID', 'count'),
        AOV=('Total_Revenue', 'mean')
    ).sort_values(by='Revenue', ascending=False)
    print(seg_summary.to_string(formatters={
        'Revenue': '${:,.2f}'.format,
        'Transactions': '{:,}'.format,
        'AOV': '${:,.2f}'.format
    }))
    
    print("\n--- TOP 5 SELLING PRODUCTS BY REVENUE ---")
    prod_summary = df.groupby('Product_Name').agg(
        Category=('Category', 'first'),
        Revenue=('Total_Revenue', 'sum'),
        Units_Sold=('Quantity', 'sum')
    ).sort_values(by='Revenue', ascending=False).head(5)
    print(prod_summary.to_string(formatters={
        'Revenue': '${:,.2f}'.format,
        'Units_Sold': '{:,}'.format
    }))
    print("-" * 60)
    
    return cat_summary, reg_summary, seg_summary

def generate_visualizations(df, vis_dir):
    print("=" * 60)
    print(" STAGE 3: GENERATING HIGH-QUALITY CHARTS")
    print("=" * 60)
    os.makedirs(vis_dir, exist_ok=True)
    
    # 1. Monthly Revenue & Transaction Trend
    df_date = df.copy()
    df_date['YearMonth'] = pd.to_datetime(df_date['Date']).dt.to_period('M')
    monthly_data = df_date.groupby('YearMonth').agg(
        Revenue=('Total_Revenue', 'sum'),
        Transactions=('Transaction_ID', 'count')
    ).reset_index()
    monthly_data['YearMonth_Str'] = monthly_data['YearMonth'].astype(str)
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Bar plot for Revenue
    color_rev = '#4A90E2'
    ax1.set_xlabel('Month', fontweight='bold', labelpad=10)
    ax1.set_ylabel('Total Revenue ($)', color=color_rev, fontweight='bold')
    bars = ax1.bar(monthly_data['YearMonth_Str'], monthly_data['Revenue'], color=color_rev, alpha=0.8, label='Monthly Revenue')
    ax1.tick_params(axis='y', labelcolor=color_rev)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.xticks(rotation=45, ha='right')
    
    # Line plot for transactions (secondary axis)
    ax2 = ax1.twinx()  
    color_tx = '#F5A623'
    ax2.set_ylabel('Transaction Volume', color=color_tx, fontweight='bold')
    line = ax2.plot(monthly_data['YearMonth_Str'], monthly_data['Transactions'], color=color_tx, marker='o', linewidth=2.5, label='Transactions')
    ax2.tick_params(axis='y', labelcolor=color_tx)
    
    plt.title('Monthly Sales Revenue and Transaction Volume Trends (2024-2025)', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    chart1_path = os.path.join(vis_dir, 'monthly_sales_trend.png')
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved: {chart1_path}")
    
    # 2. Product Category Revenue Contribution
    plt.figure(figsize=(8, 6))
    cat_rev = df.groupby('Category')['Total_Revenue'].sum().sort_values()
    colors = ['#E2849A', '#50E3C2', '#4A90E2'] # elegant contrast
    
    wedges, texts, autotexts = plt.pie(
        cat_rev, 
        labels=cat_rev.index, 
        autopct='%1.1f%%',
        startangle=140, 
        colors=colors[-len(cat_rev):],
        pctdistance=0.75,
        textprops=dict(color="black", weight="bold")
    )
    # Donut hole
    centre_circle = plt.Circle((0,0),0.55,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.title('Revenue Contribution by Product Category', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    chart2_path = os.path.join(vis_dir, 'category_revenue.png')
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved: {chart2_path}")
    
    # 3. Regional Performance Breakdown
    plt.figure(figsize=(10, 6))
    reg_perf = df.groupby('Region').agg(
        Revenue=('Total_Revenue', 'sum'),
        AOV=('Total_Revenue', 'mean')
    ).reset_index().sort_values(by='Revenue', ascending=False)
    
    ax = sns.barplot(x='Region', y='Revenue', data=reg_perf, palette='Blues_r', alpha=0.85)
    plt.title('Total Revenue Performance by Region', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Region', fontweight='bold')
    plt.ylabel('Total Revenue ($)', fontweight='bold')
    
    # Annotate bars
    for p in ax.patches:
        ax.annotate(f"${p.get_height():,.0f}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 8), 
                    textcoords='offset points', 
                    fontweight='bold', fontsize=10)
        
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.tight_layout()
    chart3_path = os.path.join(vis_dir, 'regional_performance.png')
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Saved: {chart3_path}")
    
    # 4. Customer Segment Purchase Habits (Boxplot)
    plt.figure(figsize=(10, 6))
    # Filter extreme outliers just for the visual chart scale
    df_box = df[df['Total_Revenue'] < 1500]
    sns.boxplot(x='Customer_Segment', y='Total_Revenue', data=df_box, palette=PALETTE[:3], width=0.6)
    plt.title('Distribution of Transaction Value by Customer Segment', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Customer Segment', fontweight='bold')
    plt.ylabel('Order Revenue ($) - Outliers Capped', fontweight='bold')
    plt.tight_layout()
    chart4_path = os.path.join(vis_dir, 'customer_segments.png')
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"Saved: {chart4_path}")
    print("-" * 60)

def build_ml_model(df, vis_dir):
    print("=" * 60)
    print(" STAGE 4: PREDICTIVE MACHINE LEARNING FORECASTING")
    print("=" * 60)
    
    # Convert dates to datetime
    df_ml = df.copy()
    df_ml['Date'] = pd.to_datetime(df_ml['Date'])
    
    # 1. Aggregate sales by Week (Weekly sales volume forecasting is highly robust)
    weekly_sales = df_ml.resample('W-MON', on='Date')['Total_Revenue'].sum().reset_index()
    weekly_sales = weekly_sales.sort_values(by='Date').reset_index(drop=True)
    
    print(f"Aggregated transactional sales into {len(weekly_sales)} weekly chronological intervals.")
    
    # 2. Feature Engineering: Lags & Rolling Metrics
    weekly_sales['lag_1'] = weekly_sales['Total_Revenue'].shift(1)
    weekly_sales['lag_2'] = weekly_sales['Total_Revenue'].shift(2)
    weekly_sales['lag_3'] = weekly_sales['Total_Revenue'].shift(3)
    weekly_sales['lag_4'] = weekly_sales['Total_Revenue'].shift(4)
    weekly_sales['rolling_mean_4'] = weekly_sales['Total_Revenue'].rolling(window=4).mean().shift(1)
    
    # Add calendar features
    weekly_sales['Month'] = weekly_sales['Date'].dt.month
    weekly_sales['WeekOfYear'] = weekly_sales['Date'].dt.isocalendar().week.astype(int)
    
    # Drop rows with NaNs introduced by shifts/lags
    df_features = weekly_sales.dropna().reset_index(drop=True)
    
    # 3. Prepare features and target
    feature_cols = ['lag_1', 'lag_2', 'lag_3', 'lag_4', 'rolling_mean_4', 'Month', 'WeekOfYear']
    X = df_features[feature_cols]
    y = df_features['Total_Revenue']
    
    # 4. Train-Test Split (Chronological split rather than random for time-series validity!)
    split_idx = int(len(df_features) * 0.8) # 80% train, 20% test
    
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    test_dates = df_features.loc[split_idx:, 'Date']
    
    print(f"Train samples: {len(X_train)} weeks | Test samples: {len(X_test)} weeks")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 5. Train Models: Linear Regression & Random Forest
    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=6)
    rf.fit(X_train_scaled, y_train)
    rf_pred = rf.predict(X_test_scaled)
    
    # 6. Evaluation
    def eval_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        return mae, rmse, r2
        
    lr_mae, lr_rmse, lr_r2 = eval_metrics(y_test, lr_pred)
    rf_mae, rf_rmse, rf_r2 = eval_metrics(y_test, rf_pred)
    
    print("\n--- MODEL PERFORMANCE COMPARISON ---")
    print(f"Linear Regression: MAE = ${lr_mae:,.2f} | RMSE = ${lr_rmse:,.2f} | R2 Score = {lr_r2:.3f}")
    print(f"Random Forest:     MAE = ${rf_mae:,.2f} | RMSE = ${rf_rmse:,.2f} | R2 Score = {rf_r2:.3f}")
    
    # Select the best model (using R2/RMSE)
    best_model = "Random Forest Regressor" if rf_r2 > lr_r2 else "Linear Regression"
    best_pred = rf_pred if rf_r2 > lr_r2 else lr_pred
    print(f"Selected Best Model: {best_model}")
    print("-" * 40)
    
    # 7. Plot Actual vs. Predicted Weekly Sales Time Series
    plt.figure(figsize=(12, 6))
    plt.plot(df_features['Date'], df_features['Total_Revenue'], label='Actual Sales (Historical)', color='#333333', alpha=0.5, linestyle='--')
    plt.plot(test_dates, y_test, label='Actual Sales (Test Period)', color='#4A90E2', linewidth=2, marker='o')
    plt.plot(test_dates, best_pred, label=f'Model Forecast ({best_model})', color='#F5A623', linewidth=2.5, marker='x', linestyle='-')
    
    plt.title('Weekly Sales Performance: Actual vs. Predictive Model Forecast', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Weekly Revenue ($)', fontweight='bold')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.legend(frameon=True, facecolor='white', edgecolor='none')
    plt.grid(True, alpha=0.4)
    plt.xticks(rotation=30)
    plt.tight_layout()
    
    chart5_path = os.path.join(vis_dir, 'actual_vs_predicted.png')
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f"Saved Forecast Chart: {chart5_path}")
    print("-" * 60)
    
    # Feature Importances (if RF is best)
    if best_model == "Random Forest Regressor":
        importances = rf.feature_importances_
        indices = np.argsort(importances)[::-1]
        print("\n--- FEATURE IMPORTANCE IN FORECASTING ---")
        for f in range(X.shape[1]):
            print(f"{f+1}. {feature_cols[indices[f]]:<16} : {importances[indices[f]]*100:.1f}%")
        print("-" * 60)
        
    return {
        'model_name': best_model,
        'metrics': {
            'MAE': min(lr_mae, rf_mae),
            'RMSE': min(lr_rmse, rf_rmse),
            'R2': max(lr_r2, rf_r2)
        }
    }

def main():
    base_dir = 'c:/Users/siddh/Desktop/andro/sales-insights-project'
    raw_path = os.path.join(base_dir, 'data/raw_sales_data.csv')
    clean_path = os.path.join(base_dir, 'data/cleaned_sales_data.csv')
    vis_dir = os.path.join(base_dir, 'visualizations')
    
    # 1. Clean data
    df_clean = clean_data(raw_path, clean_path)
    
    # 2. Run EDA
    perform_eda(df_clean)
    
    # 3. Generate Visualizations
    generate_visualizations(df_clean, vis_dir)
    
    # 4. Machine Learning
    build_ml_model(df_clean, vis_dir)
    
    print("\nSUCCESS: All data analysis and modeling stages completed successfully!")

if __name__ == '__main__':
    main()
