import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path


# Page configuration
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Load parquet file with caching."""
    return pd.read_parquet(file_path)


def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, color_col: str, title: str):
    """Create interactive line chart using Plotly."""
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={x_col: x_col.replace('_', ' ').title(), 
                y_col: y_col.replace('_', ' ').title()},
        template='plotly_white'
    )
    fig.update_layout(
        hovermode='x unified',
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        legend_title=color_col.replace('_', ' ').title(),
        height=500
    )
    return fig


def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color_col: str = None):
    """Create interactive bar chart using Plotly."""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={x_col: x_col.replace('_', ' ').title(), 
                y_col: y_col.replace('_', ' ').title()},
        template='plotly_white'
    )
    fig.update_layout(
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=500
    )
    return fig


def create_candlestick_chart(df: pd.DataFrame, date_col: str, ticker: str):
    """Create candlestick chart for stock prices."""
    # Filter data for specific ticker if provided
    if ticker:
        df_filtered = df[df['ticker_symbol'] == ticker].copy()
    else:
        df_filtered = df.copy()

    fig = go.Figure(data=[go.Candlestick(
        x=df_filtered[date_col],
        open=df_filtered['open_price'],
        high=df_filtered['high'],
        low=df_filtered['low'],
        close=df_filtered['close_price']
    )])

    fig.update_layout(
        title=f'Stock Price Candlestick Chart - {ticker if ticker else "All"}',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white',
        height=500,
        xaxis_rangeslider_visible=False
    )
    return fig


def main():
    """Main dashboard function."""

    # Title and description
    st.title("📈 Stock Market Analysis Dashboard")
    st.markdown("""
    This dashboard provides interactive visualizations of stock market data including:
    - Daily average close prices by ticker
    - Average volume by sector
    - Daily returns analysis
    """)

    # Sidebar for filters
    st.sidebar.header("🔍 Filters")

    try:
        # Load cleaned data
        cleaned_data = load_data('cleaned.parquet')

        # Identify column names dynamically
        date_col = [col for col in cleaned_data.columns if 'date' in col.lower()][0]
        ticker_col = [col for col in cleaned_data.columns if 'ticker' in col.lower()][0]

        # Date range filter
        st.sidebar.subheader("Date Range")
        min_date = cleaned_data[date_col].min()
        max_date = cleaned_data[date_col].max()

        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        # Ticker filter
        st.sidebar.subheader("Ticker Selection")
        all_tickers = sorted(cleaned_data[ticker_col].unique())
        selected_tickers = st.sidebar.multiselect(
            "Select tickers:",
            options=all_tickers,
            default=all_tickers[:3] if len(all_tickers) >= 3 else all_tickers
        )

        # Filter data based on selections
        if len(date_range) == 2:
            filtered_data = cleaned_data[
                (cleaned_data[date_col] >= pd.to_datetime(date_range[0])) &
                (cleaned_data[date_col] <= pd.to_datetime(date_range[1]))
            ]
        else:
            filtered_data = cleaned_data.copy()

        if selected_tickers:
            filtered_data = filtered_data[filtered_data[ticker_col].isin(selected_tickers)]

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(filtered_data))
        with col2:
            st.metric("Unique Tickers", filtered_data[ticker_col].nunique())
        with col3:
            st.metric("Date Range", f"{len(filtered_data[date_col].unique())} days")
        with col4:
            avg_volume = filtered_data[[col for col in filtered_data.columns if 'volume' in col.lower()][0]].mean()
            st.metric("Avg Volume", f"{avg_volume:,.0f}")

        # Tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Daily Close Prices", "📦 Volume by Sector", "💹 Daily Returns", "🕯️ Candlestick"])

        with tab1:
            st.header("Daily Average Close Prices by Ticker")

            try:
                agg1 = load_data('agg1_daily_avg_close.parquet')

                # Filter aggregation data
                if len(date_range) == 2:
                    agg1_filtered = agg1[
                        (agg1[date_col] >= pd.to_datetime(date_range[0])) &
                        (agg1[date_col] <= pd.to_datetime(date_range[1]))
                    ]
                else:
                    agg1_filtered = agg1.copy()

                if selected_tickers:
                    agg1_filtered = agg1_filtered[agg1_filtered[ticker_col].isin(selected_tickers)]

                # Create line chart
                fig = create_line_chart(
                    agg1_filtered,
                    x_col=date_col,
                    y_col='avg_close_price',
                    color_col=ticker_col,
                    title='Average Daily Close Price by Ticker'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Display data table
                st.subheader("Data Table")
                st.dataframe(agg1_filtered, use_container_width=True)

            except FileNotFoundError:
                st.warning("Aggregation file not found. Please run aggregation script first.")

        with tab2:
            st.header("Average Volume by Sector")

            try:
                agg2 = load_data('agg2_avg_volume_sector.parquet')

                sector_col = [col for col in agg2.columns if 'sector' in col.lower()][0]

                # Create bar chart
                fig = create_bar_chart(
                    agg2,
                    x_col=sector_col,
                    y_col='avg_volume',
                    title='Average Trading Volume by Sector',
                    color_col=sector_col
                )
                st.plotly_chart(fig, use_container_width=True)

                # Display metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Sectors", len(agg2))
                with col2:
                    st.metric("Highest Avg Volume", agg2.iloc[0][sector_col])

                # Display data table
                st.subheader("Data Table")
                st.dataframe(agg2, use_container_width=True)

            except FileNotFoundError:
                st.warning("Aggregation file not found. Please run aggregation script first.")

        with tab3:
            st.header("Daily Returns Analysis")

            try:
                agg3 = load_data('agg3_daily_return.parquet')

                # Filter aggregation data
                if len(date_range) == 2:
                    agg3_filtered = agg3[
                        (agg3[date_col] >= pd.to_datetime(date_range[0])) &
                        (agg3[date_col] <= pd.to_datetime(date_range[1]))
                    ]
                else:
                    agg3_filtered = agg3.copy()

                if selected_tickers:
                    agg3_filtered = agg3_filtered[agg3_filtered[ticker_col].isin(selected_tickers)]

                # Create line chart for returns
                fig = create_line_chart(
                    agg3_filtered,
                    x_col=date_col,
                    y_col='avg_daily_return_pct',
                    color_col=ticker_col,
                    title='Daily Return Percentage by Ticker'
                )
                fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
                st.plotly_chart(fig, use_container_width=True)

                # Display data table
                st.subheader("Data Table")
                st.dataframe(agg3_filtered, use_container_width=True)

            except FileNotFoundError:
                st.warning("Aggregation file not found. Please run aggregation script first.")

        with tab4:
            st.header("Candlestick Chart")

            # Select single ticker for candlestick
            candlestick_ticker = st.selectbox(
                "Select ticker for candlestick chart:",
                options=selected_tickers if selected_tickers else all_tickers
            )

            if candlestick_ticker:
                fig = create_candlestick_chart(filtered_data, date_col, candlestick_ticker)
                st.plotly_chart(fig, use_container_width=True)

    except FileNotFoundError:
        st.error("❌ Data files not found! Please ensure you have run the data cleaning and aggregation scripts first.")
        st.info("""
        **Steps to run:**
        1. Run `python 01_data_cleaning.py` to clean the data
        2. Run `python 02_create_aggregations.py` to create aggregations
        3. Run `streamlit run 03_streamlit_dashboard.py` to view this dashboard
        """)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()