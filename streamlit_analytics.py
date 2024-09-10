import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from dotenv import load_dotenv
import os
from src.config import PREFIX_STR 

# Load environment variables from a .env file
load_dotenv()

DATABASE_URL = os.getenv('DB_CONNECTION_STRING')

# Database connection
def get_data(query):
    conn = psycopg2.connect(DATABASE_URL)
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Convert export_date to datetime
    df['export_date'] = pd.to_datetime(df['export_date'], errors='coerce')
    return df

# Streamlit app
st.title('Shopify Data Analytics Dashboard')

# Fetch data
query = "SELECT * FROM staging.shopify_configs"
df = get_data(query)

# Data summary
st.header('Data Summary')
st.write(df.describe())
st.write(f"Number of rows: {len(df)}")

# Filter options
st.sidebar.header('Filters')
start_date = st.sidebar.date_input('Start Date', df['export_date'].min().date())
end_date = st.sidebar.date_input('End Date', df['export_date'].max().date())

filtered_df = df[(df['export_date'] >= pd.to_datetime(start_date)) & (df['export_date'] <= pd.to_datetime(end_date))]

# Pie charts for `autocomplete_enabled` and `analytics_enabled`
st.header('Feature Distributions')

col1, col2 = st.columns(2)

with col1:
    st.subheader('Autocomplete Enabled Distribution')
    autocomplete_counts = filtered_df['autocomplete_enabled'].value_counts()
    fig = px.pie(
        values=autocomplete_counts,
        names=autocomplete_counts.index,
        title='Autocomplete Enabled Distribution',
        color=autocomplete_counts.index
    )
    st.plotly_chart(fig)

with col2:
    st.subheader('Analytics Enabled Distribution')
    analytics_counts = filtered_df['analytics_enabled'].value_counts()
    fig = px.pie(
        values=analytics_counts,
        names=analytics_counts.index,
        title='Analytics Enabled Distribution',
        color=analytics_counts.index
    )
    st.plotly_chart(fig)

# Top 10 Merchandised Queries per Shop Domain
st.header('Top 10 Merchandised Queries per Shop Domain')
top_10_merchandised_queries = filtered_df.groupby('shop_domain')['nbr_merchandised_queries'].sum().nlargest(10)

# Plotly bar chart with different colors and tooltips
fig = px.bar(
    top_10_merchandised_queries,
    x=top_10_merchandised_queries.index,
    y=top_10_merchandised_queries.values,
    color=top_10_merchandised_queries.values,  # Different color for each bar
    labels={'x': 'Shop Domain', 'y': 'Total Merchandised Queries'},
    title='Top 10 Merchandised Queries per Shop Domain',
    text=top_10_merchandised_queries.values,  # Display values as text on bars
    color_continuous_scale=px.colors.sequential.Viridis  # Color scale
)

fig.update_traces(
    texttemplate='%{text:.0f}',
    textposition='outside',
    marker=dict(line=dict(color='rgb(0,0,0)', width=1))  # Border color for bars
)

fig.update_layout(
    xaxis_title='Shop Domain',
    yaxis_title='Total Merchandised Queries',
    xaxis_tickangle=-45
)

st.plotly_chart(fig)

# `install_channel`
st.header('Categorical Data')
st.subheader('Install Channel Frequency')
st.bar_chart(filtered_df['install_channel'].value_counts())

# Download option
st.header('Download Filtered Data')
st.download_button(
    label='Download CSV',
    data=filtered_df.to_csv(index=False),
    file_name='filtered_data.csv',
    mime='text/csv'
)

# Option to search by `shop_domain`
st.sidebar.header('Search by Shop Domain')
shop_domain_search = st.sidebar.text_input('Shop Domain')
if shop_domain_search:
    search_results = filtered_df[filtered_df['shop_domain'].str.contains(shop_domain_search, na=False)]
    st.write(search_results)
