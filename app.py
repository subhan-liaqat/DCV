import streamlit as st
import pandas as pd
import altair as alt
import os

# Set page to wide mode for better chart display
st.set_page_config(layout="wide")

st.title("Stock Market Analysis Dashboard")

# --- Load Data ---
# Use a function to load data and cache it for performance
@st.cache_data
def load_data():
    """Loads aggregated data from parquet files."""
    agg1_path = 'agg1.parquet'
    agg2_path = 'agg2.parquet'
    agg3_path = 'agg3.parquet'

    # Check if files exist
    if not all([os.path.exists(p) for p in [agg1_path, agg2_path, agg3_path]]):
        st.error("Data files not found. Please run 'data_processing.py' first.")
        return None, None, None

    try:
        agg_close = pd.read_parquet(agg1_path)
        agg_volume = pd.read_parquet(agg2_path)
        agg_return = pd.read_parquet(agg3_path)
        
        # Convert dates for proper filtering
        agg_close['trade_date'] = pd.to_datetime(agg_close['trade_date'])
        agg_return['trade_date'] = pd.to_datetime(agg_return['trade_date'])
        
        return agg_close, agg_volume, agg_return
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

agg_close, agg_volume, agg_return = load_data()

# Stop execution if data loading failed
if agg_close is None:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Ticker filter (multiselect)
all_tickers = sorted(agg_close['ticker'].unique())
selected_tickers = st.sidebar.multiselect(
    "Select Tickers",
    all_tickers,
    default=all_tickers[:3]  # Default to first 3 tickers
)

# Date range filter
min_date = agg_close['trade_date'].min()
max_date = agg_close['trade_date'].max()

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Handle potential error if user deselects all dates
if len(selected_date_range) != 2:
    st.sidebar.warning("Please select a start and end date.")
    st.stop()

# Convert sidebar date_input to datetime64 for filtering
start_date = pd.to_datetime(selected_date_range[0])
end_date = pd.to_datetime(selected_date_range[1])

# --- Filter Data Based on Selections ---
if not selected_tickers:
    st.warning("Please select at least one ticker.")
    st.stop()

# Apply filters
filtered_close = agg_close[
    (agg_close['ticker'].isin(selected_tickers)) &
    (agg_close['trade_date'] >= start_date) &
    (agg_close['trade_date'] <= end_date)
]

filtered_return = agg_return[
    (agg_return['ticker'].isin(selected_tickers)) &
    (agg_return['trade_date'] >= start_date) &
    (agg_return['trade_date'] <= end_date)
]

# --- Create Charts ---

# Chart 1: Average Close Price (Line Chart)
st.header("Average Daily Close Price")
if not filtered_close.empty:
    chart_close = alt.Chart(filtered_close).mark_line(point=True).encode(
        x=alt.X('trade_date', title='Date'),
        y=alt.Y('avg_close', title='Average Close Price', scale=alt.Scale(zero=False)),
        color='ticker:N',
        tooltip=['trade_date', 'ticker', 'avg_close']
    ).interactive()
    st.altair_chart(chart_close, use_container_width=True)
else:
    st.info("No 'Average Close' data available for the selected filters.")

# Chart 2: Average Volume by Sector (Bar Chart)
# This chart is not filtered by date/ticker, as it's a static aggregation
st.header("Average Volume by Sector")
if not agg_volume.empty:
    chart_volume = alt.Chart(agg_volume).mark_bar().encode(
        x=alt.X('sector', title='Sector', sort='-y'),
        y=alt.Y('avg_volume', title='Average Volume'),
        tooltip=['sector', 'avg_volume']
    ).interactive()
    st.altair_chart(chart_volume, use_container_width=True)
else:
    st.info("No 'Volume by Sector' data available.")

# Chart 3: Daily Returns (Line Chart)
st.header("Daily Returns")
if not filtered_return.empty:
    chart_return = alt.Chart(filtered_return).mark_line().encode(
        x=alt.X('trade_date', title='Date'),
        y=alt.Y('daily_return', title='Daily Return', axis=alt.Axis(format='%')),
        color='ticker:N',
        tooltip=['trade_date', 'ticker', alt.Tooltip('daily_return', format='.2%')]
    ).interactive()
    st.altair_chart(chart_return, use_container_width=True)
else:
    st.info("No 'Daily Return' data available for the selected filters.")

# Show raw filtered data (optional)
if st.checkbox("Show Filtered Data"):
    st.subheader("Filtered Close Price Data")
    st.dataframe(filtered_close)
    st.subheader("Filtered Daily Return Data")
    st.dataframe(filtered_return)
