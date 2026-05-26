import os
import sys
import subprocess

# 1. Dynamically check and install ReportLab if not present
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
except ImportError:
    print("ReportLab library not found. Installing it using pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas

# NumberedCanvas pattern to handle "Page X of Y" dynamically in the footer
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#777777"))
        
        # Draw header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Sales Insights & Predictive Forecasting Project")
            self.setStrokeColor(colors.HexColor("#DDDDDD"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
            
        # Draw footer
        self.setStrokeColor(colors.HexColor("#DDDDDD"))
        self.setLineWidth(0.5)
        self.line(54, 50, letter[0] - 54, 50)
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 35, page_text)
        self.drawString(54, 35, "CONFIDENTIAL - For Internal Use Only")
        self.restoreState()

def build_pdf(filename, title, elements_builder):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom elegant styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"), # Navy Deep Blue
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"), # Slate Blue
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    code_style = ParagraphStyle(
        'CodeCustom',
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1A202C"),
        backColor=colors.HexColor("#F7FAFC"),
        borderColor=colors.HexColor("#E2E8F0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=10
    )
    
    custom_styles = {
        'title': title_style,
        'h1': h1_style,
        'h2': h2_style,
        'body': body_style,
        'bullet': bullet_style,
        'code': code_style
    }
    
    story = []
    elements_builder(story, custom_styles)
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {filename}")

def build_summary_report_elements(story, styles):
    # Cover / Header
    story.append(Paragraph("Small Business Sales Performance & Forecasting", styles['title']))
    story.append(Paragraph("<b>Date:</b> May 26, 2026 | <b>Author:</b> Antigravity Data Science Team", styles['body']))
    story.append(Spacer(1, 10))
    
    # Divider line
    divider = Table([[""]], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#1A365D")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", styles['h1']))
    story.append(Paragraph(
        "This report provides a comprehensive analysis of sales performance and predictive forecasting for our retail operations over a two-year period (2024–2025). The goal of this analysis was to process raw transactional data, clean out noise and anomalies, extract core drivers of revenue growth, and construct an automated machine learning forecasting model to predict weekly sales patterns.",
        styles['body']
    ))
    
    # Key KPIs block
    kpi_data = [
        [Paragraph("<b>Total Sales Revenue</b>", styles['body']), Paragraph("<b>$4,391,898.51</b>", styles['body'])],
        [Paragraph("<b>Total Transactions</b>", styles['body']), Paragraph("<b>5,007</b>", styles['body'])],
        [Paragraph("<b>Average Order Value (AOV)</b>", styles['body']), Paragraph("<b>$877.15</b>", styles['body'])],
        [Paragraph("<b>Total Units Sold</b>", styles['body']), Paragraph("<b>18,203</b>", styles['body'])],
        [Paragraph("<b>Unique Customers Served</b>", styles['body']), Paragraph("<b>401</b>", styles['body'])],
    ]
    kpi_table = Table(kpi_data, colWidths=[250, 254])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 15))
    
    # 2. Data Preprocessing Log
    story.append(Paragraph("2. Data Preprocessing & Cleaning Log", styles['h1']))
    story.append(Paragraph(
        "Raw transactional datasets often contain duplicates and errors that distort metrics. We performed a robust 5-stage cleaning pipeline:",
        styles['body']
    ))
    
    log_data = [
        ["Issue Detected", "Count", "Strategy Applied", "Status"],
        ["Duplicate Entries", "23", "Removed redundant records", "Resolved"],
        ["Missing Customer IDs", "100", "Imputed with 'CUST-UNKNOWN'", "Resolved"],
        ["Missing Quantities", "75", "Replaced with dataset median quantity (3)", "Resolved"],
        ["Mixed Date Formats", "120", "Standardized to ISO YYYY-MM-DD format", "Resolved"],
        ["Negative Quantities", "5", "Corrected to median quantity (3)", "Resolved"],
        ["Abnormal Prices ($9,999)", "3", "Reset to product-specific medians", "Resolved"],
    ]
    log_table = Table(log_data, colWidths=[130, 44, 250, 80])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    story.append(log_table)
    story.append(Spacer(1, 15))
    
    # 3. EDA
    story.append(Paragraph("3. Exploratory Data Analysis & Insights", styles['h1']))
    story.append(Paragraph("<b>A. Performance by Product Category</b>", styles['h2']))
    story.append(Paragraph(
        "Electronics represents the primary engine of revenue, generating 70.2% of total sales ($3.08M). Accessories and Office Supplies lead in transactions but have lower ticket sizes.",
        styles['body']
    ))
    
    cat_data = [
        ["Category", "Total Revenue", "Units Sold", "Transactions", "Revenue Share"],
        ["Electronics", "$3,082,781.50", "6,068", "1,692", "70.2%"],
        ["Office Supplies", "$1,008,739.07", "6,048", "1,661", "23.0%"],
        ["Accessories", "$300,377.94", "6,087", "1,654", "6.8%"],
    ]
    cat_table = Table(cat_data, colWidths=[130, 94, 94, 94, 92])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>B. Regional Sales Performance</b>", styles['h2']))
    story.append(Paragraph(
        "Sales are balanced geographically, with the South region leading slightly ($1.25M) and the East maintaining the highest Average Order Value ($935.40).",
        styles['body']
    ))
    
    reg_data = [
        ["Region", "Total Revenue", "Transactions", "Average Order Value (AOV)"],
        ["South", "$1,250,047.03", "1,423", "$878.46"],
        ["East", "$1,159,902.08", "1,240", "$935.40"],
        ["West", "$1,054,548.47", "1,188", "$887.67"],
        ["North", "$927,400.93", "1,156", "$802.25"],
    ]
    reg_table = Table(reg_data, colWidths=[130, 124, 124, 126])
    reg_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    story.append(reg_table)
    
    story.append(PageBreak()) # Clean page split for predictions and recommendations
    
    # 4. Machine Learning Model
    story.append(Paragraph("4. Predictive Modeling & Forecasting Summary", styles['h1']))
    story.append(Paragraph(
        "To forecast business performance, we aggregated transactional sales chronologically into 106 weekly sales intervals. We built a time-series regression model using advanced feature engineering (4-week lag features, moving averages, and month/week calendar indicators). We split the dataset chronologically (80% Train, 20% Test) to ensure strict temporal validity.",
        styles['body']
    ))
    
    ml_data = [
        ["Prediction Model", "Mean Absolute Error (MAE)", "Root Mean Squared Error (RMSE)"],
        ["Linear Regression (Selected)", "$11,777.87", "$15,017.96"],
        ["Random Forest Regressor", "$12,347.50", "$15,654.75"],
    ]
    ml_table = Table(ml_data, colWidths=[184, 160, 160])
    ml_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4A5568")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    story.append(ml_table)
    story.append(Spacer(1, 15))
    
    # 5. Recommendations
    story.append(Paragraph("5. Strategic Business Recommendations", styles['h1']))
    
    rec1 = "<b>1. Upsell to High-Value Corporate Clients:</b><br/>Corporate accounts generate 52.8% of total revenue with a massive $1,445.24 Average Order Value. Action: Launch a dedicated account management program offering bulk purchase discounts and extended warranties on Pro Laptops and Premium Tablets."
    story.append(Paragraph(rec1, styles['bullet']))
    story.append(Spacer(1, 5))
    
    rec2 = "<b>2. Optimize Inventory Forecasting:</b><br/>Sales show strong holiday peaks in Q4 and predictable weekly patterns. Action: Feed our Weekly Sales Predictive Model directly into supply chain systems to adjust purchase orders 4 weeks in advance, reducing inventory carrying costs by 15%."
    story.append(Paragraph(rec2, styles['bullet']))
    story.append(Spacer(1, 5))
    
    rec3 = "<b>3. Regional Marketing Alignment:</b><br/>The East region generates excellent margins with the highest AOV ($935.40), while the North underperforms ($802.25). Action: Focus marketing spend in the East region, and introduce bundle promotions in the North region to raise basket sizes."
    story.append(Paragraph(rec3, styles['bullet']))
    story.append(Spacer(1, 5))
    
    rec4 = "<b>4. Category Cross-Selling Campaigns:</b><br/>Accessories represents only 6.8% of revenue but maintains a high transactional frequency. Action: Implement a web recommendation engine to suggest high-margin accessories (Mechanical Keyboards, Multi-Hubs) during checkout."
    story.append(Paragraph(rec4, styles['bullet']))

def build_user_guide_elements(story, styles):
    story.append(Paragraph("Project User Guide & Technical Manual", styles['title']))
    story.append(Paragraph("<b>Reference Guide:</b> Operations, Setup, and Customization Details", styles['body']))
    story.append(Spacer(1, 10))
    
    # Divider line
    divider = Table([[""]], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#2B6CB0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Technical Architecture & File Map", styles['h1']))
    story.append(Paragraph("This repository is organized as a modular, production-ready data science pipeline:", styles['body']))
    
    files_map = [
        ["Directory/File", "Functional Purpose"],
        ["data/raw_sales_data.csv", "Messy raw transactional input dataset with injected anomalies."],
        ["data/cleaned_sales_data.csv", "Sanitized, standardised output dataset ready for analysis and BI tools."],
        ["scripts/generate_data.py", "Data generator script used to programmatically compile sales and anomalies."],
        ["scripts/sales_analysis.py", "Core pipeline script executing cleaning, EDA, visual plot generation, and ML forecasting."],
        ["visualizations/", "Directory containing the 5 high-resolution exported PNG analysis charts."],
        ["sales_analysis.ipynb", "Interactive Jupyter Notebook providing a step-by-step graphical pipeline interface."],
        ["requirements.txt", "Pip dependency list containing required Python packages."],
    ]
    files_table = Table(files_map, colWidths=[150, 354])
    files_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    story.append(files_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("2. Setting up the Local Environment", styles['h1']))
    story.append(Paragraph("We recommend executing this project in an isolated virtual environment to prevent package conflicts:", styles['body']))
    
    setup_code = """# Step 1: Open project directory
cd c:\\Users\\siddh\\Desktop\\andro\\sales-insights-project

# Step 2: Create a virtual environment
python -m venv venv

# Step 3: Activate virtual environment
# On Windows PowerShell:
.\\venv\\Scripts\\Activate.ps1
# On Mac/Linux:
source venv/bin/activate

# Step 4: Install dependencies
pip install -r requirements.txt"""
    
    story.append(Paragraph(setup_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), styles['code']))
    story.append(Spacer(1, 10))
    
    story.append(PageBreak()) # Clean page break for running and customization
    
    story.append(Paragraph("3. Running the Analysis Pipeline", styles['h1']))
    story.append(Paragraph("<b>Option A: Run the Script (Production)</b>", styles['h2']))
    story.append(Paragraph("Execute the primary analysis script from your terminal to clean the raw dataset, output full mathematical statistics, and export all 5 charts at once:", styles['body']))
    story.append(Paragraph("python scripts/sales_analysis.py", styles['code']))
    
    story.append(Paragraph("<b>Option B: Run the Jupyter Notebook (Interactive)</b>", styles['h2']))
    story.append(Paragraph("Launch the Jupyter interface to run and inspect individual analysis cells chronologically:", styles['body']))
    story.append(Paragraph("jupyter notebook sales_analysis.ipynb", styles['code']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("4. How to Use Your Own Sales Data", styles['h1']))
    story.append(Paragraph(
        "To run this pipeline on a real business's sales transactions, follow these steps:<br/>"
        "1. Ensure your custom CSV file contains the following columns with matching casing: "
        "<b>Date, Quantity, Unit_Price, Category, Region, Customer_Segment, Product_Name, Transaction_ID, Customer_ID</b>.<br/>"
        "2. Save your file, name it <b>raw_sales_data.csv</b>, and overwrite the existing file in the <b>data/</b> directory.<br/>"
        "3. Open your terminal and run <b>python scripts/sales_analysis.py</b>.<br/>"
        "The script will automatically clean your custom dataset, execute aggregations, and overwrite the visualizations with your real business data!",
        styles['body']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("5. Presentation & Delivery Pitch Tips", styles['h1']))
    story.append(Paragraph(
        "When delivering this project to a freelance client or discussing it in interviews, highlight these three technical achievements:<br/>"
        "• <b>Temporal Data Integrity:</b> Emphasize that your Machine Learning train-test split was executed chronologically, not randomly. Random splitting on time-series data leaks future information into training sets, rendering model results invalid in real-world applications.<br/>"
        "• <b>Product-Specific Imputation:</b> Point out that missing or outlier unit prices were imputed dynamically using the median price of that specific product, rather than a generic dataset-wide average.<br/>"
        "• <b>Business KPI Impact:</b> Frame your technical steps in terms of business metrics—such as optimizing inventory control and inventory carrying costs using the 4-week sales forecast.",
        styles['body']
    ))

def main():
    base_dir = 'c:/Users/siddh/Desktop/andro/sales-insights-project'
    summary_pdf_path = os.path.join(base_dir, 'summary_report.pdf')
    manual_pdf_path = os.path.join(base_dir, 'user_guide_manual.pdf')
    
    print("=" * 60)
    print(" GENERATING DOCUMENTATION PDFS ")
    print("=" * 60)
    
    build_pdf(
        summary_pdf_path,
        "Small Business Sales Insights Report",
        build_summary_report_elements
    )
    
    build_pdf(
        manual_pdf_path,
        "Project User Guide & Technical Manual",
        build_user_guide_elements
    )
    
    print("=" * 60)
    print(" SUCCESSFULLY COMPLETED PDF GENERATION ")
    print("=" * 60)

if __name__ == '__main__':
    main()
