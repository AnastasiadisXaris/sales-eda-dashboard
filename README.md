# sales-eda-dashboard
# 📊 Sales Data EDA Dashboard

An interactive Streamlit dashboard that allows you to upload and explore your own sales data through visual analytics and automated insights.

## 🚀 Features

- Upload your own CSV file with sales data
- Clean and preprocess the data automatically
- View sales trends by month, product, city
- Correlation heatmaps for numeric variables
- Time series analysis of sales over time

## 📁 Sample CSV Format

Your CSV file should include columns like:
- `Order Date` (e.g., 2023-01-15)
- `Product`
- `Quantity Ordered`
- `Price Each`
- `City` (optional)

## 🛠 How to Run Locally

```bash
git clone https://github.com/your-username/sales-eda-dashboard.git
cd sales-eda-dashboard
pip install -r requirements.txt
streamlit run app.py

