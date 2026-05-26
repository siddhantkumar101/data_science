# Project User Guide & Technical Manual: Sales Insights & Forecasting

Welcome to your **Sales Insights & Forecasting** project! This guide provides everything you need to know to run the project properly, interpret its results, customize it for other datasets, and pitch it to freelance clients or interviewers.

---

## 1. Project Directory & Architecture Map

Here is the functional purpose of every file in your repository:

* **`data/`**
  * `raw_sales_data.csv`: The uncleaned input dataset containing synthetic transactional records and pre-programmed anomalies (duplicates, missing cells, outlier values, and mixed date formats).
  * `cleaned_sales_data.csv`: The output dataset after executing the cleaning script. It is standard, uniform, complete, and optimized for databases or BI software (like Tableau/PowerBI).
* **`scripts/`**
  * `generate_data.py`: A utility script that programmatically compiles the sales transactions and injects seasonal trends alongside dirty data.
  * `sales_analysis.py`: The core engine of the project. It handles data cleaning, computes statistics, exports the 5 PNG charts, and trains the machine learning forecasting models.
* **`visualizations/`**
  * `monthly_sales_trend.png`: A double-axis graph tracking total revenue and order volume monthly.
  * `category_revenue.png`: A clean donut chart showing category sales percentages.
  * `regional_performance.png`: Total sales revenue grouped by geographical regions.
  * `customer_segments.png`: A box plot distributing order sizes across Corporate, Small Business, and Consumer channels.
  * `actual_vs_predicted.png`: A line chart comparing actual test-period sales against the ML model's forecast.
* **`sales_analysis.ipynb`**: An interactive Jupyter Notebook serving as a visual interface for running code blocks step-by-step.
* **`requirements.txt`**: A list of Python libraries needed to execute the codebase.
* **`summary_report.md`** & **`README.md`**: Business summary report highlighting the key findings and strategic actions.

---

## 2. Step-by-Step Local Execution Guide

### Option A: Running from the Command Line (Fastest)

1. **Open your Terminal/PowerShell** and navigate to your project:
   ```bash
   cd c:\Users\siddh\Desktop\andro\sales-insights-project
   ```
2. **Set up a Virtual Environment (Best Practice)**:
   This isolates the project libraries from your global Python environment to prevent conflicts:
   ```bash
   python -m venv venv
   ```
3. **Activate the Virtual Environment**:
   * *Windows (PowerShell)*: `.\venv\Scripts\Activate.ps1`
   * *Windows (CMD)*: `.\venv\Scripts\activate.bat`
   * *Mac/Linux*: `source venv/bin/activate`
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Analysis Pipeline**:
   ```bash
   python scripts/sales_analysis.py
   ```
   *(This will clean the raw data, print complete statistical outputs to your screen, and generate the updated charts).*

---

### Option B: Running Interactively via Jupyter Notebook

1. **Activate your Virtual Environment** (as shown above).
2. **Start the Jupyter Server**:
   ```bash
   jupyter notebook
   ```
3. Open your browser and select **`sales_analysis.ipynb`**.
4. Click **Cell > Run All** from the top menu. This will execute the analysis code and display the charts inline inside your notebook interface.

---

## 3. Deep Dive into the Visual & ML Outputs

When you run the pipeline, it outputs 5 professional charts. Here is how to explain what they represent:

### 1. Monthly Revenue & Transaction Trend (`monthly_sales_trend.png`)
* **What it shows:** Total revenue per month (blue columns) plotted against transaction counts (orange line).
* **Key Takeaway:** Highlights annual seasonality (e.g., Q4 holiday spikes in November and December) and whether revenue growth is driven by *more orders* or *larger order values*.

### 2. Category Revenue Share (`category_revenue.png`)
* **What it shows:** A donut chart dividing total sales among Electronics, Office Supplies, and Accessories.
* **Key Takeaway:** Shows which product segments represent the "anchor" of your company (Electronics at 70.2%) versus transactional volume headers (Accessories).

### 3. Regional Sales Performance (`regional_performance.png`)
* **What it shows:** Vertical bar chart showing total revenue per region (South, East, West, North).
* **Key Takeaway:** Identifies geographic strengths and opportunities (e.g., target marketing spend in underperforming regions like the North).

### 4. Segment Transaction Distribution (`customer_segments.png`)
* **What it shows:** A box-and-whisker plot of order sizes grouped by customer segment.
* **Key Takeaway:** Demonstrates purchasing behaviors. Corporate segments have a much wider distribution and a significantly higher median transaction size ($1,445 AOV), while Consumers buy small values frequently.

### 5. Sales Forecast Verification (`actual_vs_predicted.png`)
* **What it shows:** Weekly sales during the historical test period (blue line) vs. the model's weekly predictions (orange line).
* **Key Takeaway:** Displays how closely the **Linear Regression/Random Forest** models are learning temporal patterns. A model tracking the spikes and drops shows strong predictive capacity.

---

## 4. How to Use Your Own (Real) Sales Data 📈

You can easily adapt this project to analyze a real company's sales data!

### File Requirements:
Your input CSV file must contain these columns (with matching spelling and casing):
* `Date` (Format: `YYYY-MM-DD` or `MM/DD/YYYY`)
* `Quantity` (Integer numbers)
* `Unit_Price` (Decimal pricing numbers)
* `Category` (Categorical groupings, e.g. Electronics)
* `Region` (Geographical locations)
* `Customer_Segment` (e.g., Corporate, Consumer)
* `Product_Name`
* `Transaction_ID`
* `Customer_ID`

### How to Swap the Data:
1. Copy your real sales dataset CSV file.
2. Rename it to **`raw_sales_data.csv`** and paste it inside the **`data/`** directory (overwriting the existing file).
3. Open your terminal and run the pipeline script:
   ```bash
   python scripts/sales_analysis.py
   ```
4. The script will automatically clean your new dataset, print the new statistics, re-train the machine learning models on your custom timeline, and overwrite the visualizations with your real charts!

---

## 5. Client & Interview Presentation Pitch

Use this structured guide when presenting this project to clients or interviewers to highlight your technical and business communication skills:

### The Problem-Solution Frame:
> *"I built a complete data science pipeline designed to solve a very common small business issue: dirty, unorganized transactional logs that prevent clear business visibility. I generated a raw transactional dataset with mixed formats, missing customer fields, pricing typos, and duplicate logs. I then implemented a robust python preprocessing system to sanitize the data.*
>
> *Once cleaned, I conducted deep EDA, extracting critical growth drivers like Corporate accounts representing over 52% of total revenue despite lower volumes. Finally, I built an autoregressive weekly sales forecasting model in Scikit-Learn that allows inventory managers to anticipate supply demands up to 4 weeks in advance, directly impacting cash flow and storage efficiency."*

### Key Features to Emphasize:
1. **Chronological Splitting in ML**: Point out that you split the training/test datasets *chronologically (80% early weeks, 20% recent weeks)* rather than randomly. Random splitting causes data leakage in time-series forecasting; a temporal split is the industry best practice.
2. **Text Standardization**: Discuss how you handled messy user inputs (like trailing spaces and mixed cases like " accessories" vs. "Electronics ") to ensure group aggregations were mathematically accurate.
3. **Product-Specific Imputation**: Highlight that when filling missing or outlier prices, you didn't just use a generic average. You calculated the median price *per specific product*, ensuring that a missing tablet price wasn't mistakenly filled with a cheap pen price.
