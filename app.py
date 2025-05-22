import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set(style="whitegrid")

st.set_page_config(page_title="Sales EDA Dashboard", layout="wide")
st.title("📊 Sales Data EDA Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("📄 Raw Data")
    st.dataframe(df.head())

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

    st.subheader("📊 Summary Statistics")
    st.write(df.describe())

    # Sidebar filters
    st.sidebar.header("Filters")
    if 'Year' in df.columns:
        selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].dropna().unique()))
        df = df[df['Year'] == selected_year]

    # Monthly Sales
    if 'Month' in df.columns and 'Total Sales' in df.columns:
        st.subheader("🗓️ Monthly Sales")
        monthly_sales = df.groupby('Month')['Total Sales'].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(data=monthly_sales, x='Month', y='Total Sales', ax=ax)
        st.pyplot(fig)

    # Top Products
    if 'Product' in df.columns and 'Quantity Ordered' in df.columns:
        st.subheader("📦 Top Selling Products")
        top_products = df.groupby('Product')['Quantity Ordered'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 4))
        top_products.plot(kind='bar', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Sales by City
    if 'City' in df.columns:
        st.subheader("🏙️ Sales by City")
        city_sales = df.groupby('City')['Total Sales'].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 4))
        city_sales.plot(kind='bar', ax=ax, color='teal')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Time Series Analysis
    if 'Order Date' in df.columns and 'Total Sales' in df.columns:
        st.subheader("📈 Sales Over Time")
        daily_sales = df.groupby('Order Date')['Total Sales'].sum()
        fig, ax = plt.subplots(figsize=(14, 4))
        daily_sales.plot(ax=ax)
        plt.ylabel("Total Sales")
        plt.xlabel("Date")
        st.pyplot(fig)

    # Correlation Heatmap
    st.subheader("🔍 Correlation Heatmap")
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

else:
    st.info("👆 Please upload a CSV file to begin analysis.")
