import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_raw_data(output_path, num_records=5000):
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)

    # 1. Base lists
    products = {
        'Electronics': {
            'Pro Laptop': 1200.0,
            'Premium Tablet': 600.0,
            'Noise-Cancelling Headphones': 250.0,
            'Smartwatch': 200.0,
            '4K Monitor': 350.0
        },
        'Office Supplies': {
            'Ergonomic Chair': 299.99,
            'Standing Desk': 450.0,
            'Premium Notebook': 15.5,
            'Gel Pens 12-Pack': 12.99,
            'Whiteboard': 79.99
        },
        'Accessories': {
            'Wireless Mouse': 49.99,
            'Mechanical Keyboard': 99.99,
            'USB-C Multi-Hub': 39.99,
            'Desk Mat': 25.0,
            'Laptop Sleeve': 29.99
        }
    }
    
    categories = list(products.keys())
    regions = ['North', 'South', 'East', 'West']
    segments = ['Consumer', 'Corporate', 'Small Business']
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash']
    
    # Generate static customer pool to show repeat purchases
    customer_ids = [f"CUST-{i:04d}" for i in range(1, 401)]
    # Assign a fixed region and segment to each customer for realism
    customer_profiles = {}
    for cid in customer_ids:
        customer_profiles[cid] = {
            'Region': random.choice(regions),
            'Segment': random.choice(segments)
        }

    # Time frame: Jan 1, 2024 to Dec 31, 2025 (2 years)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days

    data = []
    
    for i in range(num_records):
        tx_id = f"TX-{10000 + i}"
        
        # Determine Date with seasonal weight
        # Add random number of days
        random_days = random.randint(0, date_range_days)
        tx_date = start_date + timedelta(days=random_days)
        
        # Add seasonal adjustments: Q4 (Oct, Nov, Dec) gets 40% more traffic
        if tx_date.month in [10, 11, 12]:
            if random.random() < 0.25: # 25% chance to duplicate dates or boost Q4 further
                tx_date = tx_date + timedelta(hours=random.randint(0, 23))
        
        # Add weekend boost
        if tx_date.weekday() in [5, 6]: # Sat, Sun
            if random.random() < 0.15:
                # Add another order on weekend
                pass

        # Select Customer
        cust_id = random.choice(customer_ids)
        profile = customer_profiles[cust_id]
        region = profile['Region']
        segment = profile['Segment']
        
        # Select Product
        category = random.choice(categories)
        prod_list = list(products[category].keys())
        product_name = random.choice(prod_list)
        unit_price = products[category][product_name]
        
        # Quantity based on segment and category
        if segment == 'Corporate':
            quantity = random.randint(2, 10)
        else:
            quantity = random.randint(1, 4)
            
        payment = random.choice(payment_methods)
        
        # Add realistic variability to unit price (discounts)
        discount = 0.0
        if random.random() < 0.2: # 20% transactions have discount
            discount = round(random.uniform(0.05, 0.20), 2) # 5% to 20% discount
            
        final_unit_price = round(unit_price * (1 - discount), 2)
        
        data.append({
            'Transaction_ID': tx_id,
            'Date': tx_date.strftime('%Y-%m-%d'),
            'Customer_ID': cust_id,
            'Product_Name': product_name,
            'Category': category,
            'Quantity': quantity,
            'Unit_Price': final_unit_price,
            'Region': region,
            'Customer_Segment': segment,
            'Payment_Method': payment
        })
        
    df = pd.DataFrame(data)
    
    # 2. INJECT ANOMALIES & DIRTiness
    
    # A. Introduce duplicate rows (~30 duplicates)
    dup_indices = np.random.choice(df.index, size=30, replace=False)
    dup_rows = df.loc[dup_indices].copy()
    # adjust transaction IDs so they look like exact duplicates or double-entries
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # B. Introduce missing values (~3% missing for critical fields)
    # Customer_ID missing
    cust_missing_idx = np.random.choice(df.index, size=int(len(df) * 0.02), replace=False)
    df.loc[cust_missing_idx, 'Customer_ID'] = np.nan
    
    # Quantity missing
    qty_missing_idx = np.random.choice(df.index, size=int(len(df) * 0.015), replace=False)
    df.loc[qty_missing_idx, 'Quantity'] = np.nan
    
    # Region missing
    region_missing_idx = np.random.choice(df.index, size=int(len(df) * 0.025), replace=False)
    df.loc[region_missing_idx, 'Region'] = None
    
    # C. Introduce text formatting issues (trailing spaces, mixed cases)
    # Trailing spaces in category names
    df.loc[df['Category'] == 'Electronics', 'Category'] = 'Electronics '
    df.loc[df['Category'] == 'Accessories', 'Category'] = ' accessories' # mixed case & leading space
    
    # Leading/trailing spaces in Region
    df.loc[df['Region'] == 'North', 'Region'] = ' North '
    df.loc[df['Region'] == 'South', 'Region'] = 'south' # lowercase
    
    # D. Inconsistent date formats (~100 records formatted as MM/DD/YYYY)
    date_bad_idx = np.random.choice(df.index, size=120, replace=False)
    for idx in date_bad_idx:
        curr_date_str = df.loc[idx, 'Date']
        if pd.notna(curr_date_str):
            dt = datetime.strptime(curr_date_str, '%Y-%m-%d')
            df.loc[idx, 'Date'] = dt.strftime('%m/%d/%Y')
            
    # E. Introduce outliers and typos
    # Outliers in Quantity (negative values and huge values)
    outlier_qty_idx1 = np.random.choice(df.index, size=5, replace=False)
    df.loc[outlier_qty_idx1, 'Quantity'] = -2
    outlier_qty_idx2 = np.random.choice(df.index, size=3, replace=False)
    df.loc[outlier_qty_idx2, 'Quantity'] = 150 # abnormally large quantity for retail
    
    # Outliers in Unit_Price (abnormally high or 0)
    outlier_price_idx1 = np.random.choice(df.index, size=4, replace=False)
    df.loc[outlier_price_idx1, 'Unit_Price'] = 0.0
    outlier_price_idx2 = np.random.choice(df.index, size=3, replace=False)
    df.loc[outlier_price_idx2, 'Unit_Price'] = 9999.99 # typo price
    
    # Shuffle the dataframe to make the anomalies scattered
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save raw CSV
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully! Total rows: {len(df)}")
    print(f"Saved to: {output_path}")

if __name__ == '__main__':
    generate_raw_data('c:/Users/siddh/Desktop/andro/sales-insights-project/data/raw_sales_data.csv')
