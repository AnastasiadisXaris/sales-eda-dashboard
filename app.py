import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Set Seaborn style
sns.set(style="whitegrid")

st.set_page_config(page_title="Sales EDA Dashboard", layout="wide")
st.title("📊 Sales Data EDA Dashboard")

# File uploader
uploaded_file = st.file_uploader("Φόρτωσε το αρχείο σου CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Data Preprocessing
    with st.spinner("Cleaning data..."):
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
            df.dropna(subset=['Order Date'], inplace=True)
            df['Month'] = df['Order Date'].dt.month
            df['Year'] = df['Order Date'].dt.year
            df['Day'] = df['Order Date'].dt.day_name()

        if 'Quantity Ordered' in df.columns and 'Price Each' in df.columns:
            df['Total Sales'] = df['Quantity Ordered'] * df['Price Each']

    # Sidebar filters
    st.sidebar.header("📌 Filters")

    if 'Year' in df.columns:
        year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique()))
        df = df[df['Year'] == year]

    if 'Product' in df.columns:
        products = st.sidebar.multiselect("Select Products", options=df['Product'].unique(), default=df['Product'].unique())
        df = df[df['Product'].isin(products)]

    if 'City' in df.columns:
        cities = st.sidebar.multiselect("Select Cities", options=df['City'].unique(), default=df['City'].unique())
        df = df[df['City'].isin(cities)]

    if 'Order Date' in df.columns:
        min_date = df['Order Date'].min()
        max_date = df['Order Date'].max()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        if len(date_range) == 2:
            df = df[(df['Order Date'] >= pd.to_datetime(date_range[0])) & (df['Order Date'] <= pd.to_datetime(date_range[1]))]

    # KPI Cards
    st.subheader("📌 Key Performance Indicators")
    total_sales = df['Total Sales'].sum() if 'Total Sales' in df.columns else 0
    total_orders = len(df)
    avg_order_value = total_sales / total_orders if total_orders else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders}")
    col3.metric("Avg. Order Value", f"${avg_order_value:,.2f}")

    # Raw Data
    with st.expander("📄 Show Raw Data"):
        st.dataframe(df.head(100))
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Data", data=csv, file_name="filtered_sales_data.csv", mime='text/csv')

    # Monthly Sales
    if 'Month' in df.columns and 'Total Sales' in df.columns:
        st.subheader("🗓️ Monthly Sales")
        chart_type = st.selectbox("Chart Type for Monthly Sales", ['Bar', 'Line', 'Pie'], key='monthly')
        monthly_sales = df.groupby('Month')['Total Sales'].sum().reset_index()

        fig, ax = plt.subplots()
        if chart_type == 'Bar':
            sns.barplot(data=monthly_sales, x='Month', y='Total Sales', palette='Blues_d', ax=ax)
        elif chart_type == 'Line':
            ax.plot(monthly_sales['Month'], monthly_sales['Total Sales'], marker='o')
        elif chart_type == 'Pie':
            ax.pie(monthly_sales['Total Sales'], labels=monthly_sales['Month'], autopct='%1.1f%%')
        st.pyplot(fig)

    # Top Products
    if 'Product' in df.columns and 'Quantity Ordered' in df.columns:
        st.subheader("📦 Top Selling Products")
        chart_type = st.selectbox("Chart Type for Top Products", ['Bar', 'Line', 'Pie'], key='top_products')
        top_products = df.groupby('Product')['Quantity Ordered'].sum().sort_values(ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 4))
        if chart_type == 'Bar':
            top_products.plot(kind='bar', ax=ax, color='orange')
        elif chart_type == 'Line':
            top_products.plot(ax=ax, marker='o', color='orange')
        elif chart_type == 'Pie':
            ax.pie(top_products.values, labels=top_products.index, autopct='%1.1f%%')
        st.pyplot(fig)

    # Sales by City
    if 'City' in df.columns:
        st.subheader("🏙️ Sales by City")
        chart_type = st.selectbox("Chart Type for City Sales", ['Bar', 'Line', 'Pie'], key='city_sales')
        city_sales = df.groupby('City')['Total Sales'].sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 4))
        if chart_type == 'Bar':
            city_sales.plot(kind='bar', ax=ax, color='teal')
        elif chart_type == 'Line':
            city_sales.plot(ax=ax, marker='o', color='teal')
        elif chart_type == 'Pie':
            ax.pie(city_sales.values, labels=city_sales.index, autopct='%1.1f%%')
        st.pyplot(fig)

    # Time Series Analysis
    if 'Order Date' in df.columns and 'Total Sales' in df.columns:
        st.subheader("📈 Sales Over Time")
        daily_sales = df.groupby('Order Date')['Total Sales'].sum()
        fig, ax = plt.subplots(figsize=(14, 4))
        daily_sales.plot(ax=ax)
        ax.set_ylabel("Total Sales")
        ax.set_xlabel("Date")
        ax.set_title("Daily Sales")
        st.pyplot(fig)

    # Correlation Heatmap
    st.subheader("🔍 Correlation Heatmap")
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    # Pivot Analysis
    st.subheader("📊 Pivot Table Analysis")
    group_col = st.selectbox("Group by:", options=df.columns, index=0)
    agg_col = st.selectbox("Aggregate column:", options=numeric_df.columns, index=0)
    agg_func = st.selectbox("Aggregation function:", options=['sum', 'mean', 'count', 'max', 'min'], index=0)

    if group_col and agg_col and agg_func:
        pivot_table = df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
        st.dataframe(pivot_table)
        csv_pivot = pivot_table.to_csv(index=False).encode('utf-8')
        st.download_button("Download Pivot Table", data=csv_pivot, file_name="pivot_table.csv", mime='text/csv')

else:
    st.info("👆 Παρακαλώ φόρτωσε το αρχείο σου CSV για να ξεκινήσει η ανάλυση.")
