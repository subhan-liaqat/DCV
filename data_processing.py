import pandas as pd
import numpy as np
import re
import sys

def clean_column_name(col):
    """Converts column name to snake_case, trims, and lowers."""
    col = col.strip()  # Trim whitespace
    col = col.lower()  # Convert to lowercase
    col = re.sub(r'\s+', '_', col)  # Replace spaces with underscores
    col = re.sub(r'[^a-zA-Z0-9_]', '', col)  # Remove non-alphanumeric
    return col

def process_data(file_name):
    """
    Loads, cleans, and aggregates stock market data.
    """
    print("Starting data processing...")

    # === Step 1 & 2: Load and Normalize Schema ===
    
    # Define standard values to treat as null, including 'na'
    na_values = ["", "NA", "N/A", "null", "-", " ", "na"]
    
    try:
        df = pd.read_csv(file_name, na_values=na_values)
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Loaded raw data. Shape: {df.shape}")
    
    # Normalize schema (headers)
    df.columns = [clean_column_name(col) for col in df.columns]
    print(f"Normalized columns: {df.columns.to_list()}")

    # === Step 3: Fix Formats, Deduplicate, Save Cleaned ===

    # Trim whitespace and lowercase string columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].str.strip().str.lower()

    # Fix date format (from MM/DD/YYYY)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%m/%d/%Y', errors='coerce')
    
    # Convert numeric columns, coercing errors to NaN
    numeric_cols = ['open_price', 'close_price', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert 'volume' to nullable integer (supports <NA>)
    df['volume'] = df['volume'].astype('Int64')

    # Fix boolean 'validated' column
    bool_map = {'yes': True, 'y': True, 'no': False, 'n': False}
    df['validated'] = df['validated'].map(bool_map).astype('boolean') # Use nullable boolean
    
    print("Standardized data types (date, numeric, boolean).")
    
    # Drop rows where key identifiers are null
    initial_rows = df.shape[0]
    df.dropna(subset=['trade_date', 'ticker', 'close_price'], inplace=True)
    print(f"Dropped {initial_rows - df.shape[0]} rows with null essential data (date, ticker, or close price).")
    
    # Deduplicate rows
    initial_rows = df.shape[0]
    df.drop_duplicates(inplace=True)
    print(f"Deduplicated: {initial_rows - df.shape[0]} rows removed.")

    # Store the cleaned file
    try:
        df.to_parquet('cleaned.parquet', index=False, engine='pyarrow')
        print("Successfully saved 'cleaned.parquet'.")
    except ImportError:
        print("\n*** 'pyarrow' library not found. Cannot save parquet file. ***")
        print("Please install it by running: pip install pyarrow")
    except Exception as e:
        print(f"Error saving 'cleaned.parquet': {e}")
        return

    # === Step 4: Create and Save Aggregations ===

    print("\nCreating aggregations...")

    # Load from the parquet file for consistency
    try:
        df_clean = pd.read_parquet('cleaned.parquet')
    except Exception as e:
        print(f"Error reading 'cleaned.parquet'. Aborting aggregations. {e}")
        return

    # Agg 1: Daily avg close by ticker
    agg1 = df_clean.groupby(['ticker', 'trade_date'])['close_price'].mean().reset_index()
    agg1 = agg1.rename(columns={'close_price': 'avg_close'})
    agg1.to_parquet('agg1.parquet', index=False)
    print("Saved 'agg1.parquet' (daily avg close by ticker).")

    # Agg 2: Avg volume by sector (ignoring rows with null sectors)
    agg2 = df_clean.dropna(subset=['sector']).groupby('sector')['volume'].mean().reset_index()
    agg2 = agg2.rename(columns={'volume': 'avg_volume'})
    agg2.to_parquet('agg2.parquet', index=False)
    print("Saved 'agg2.parquet' (avg volume by sector).")

    # Agg 3: Simple daily return by ticker
    df_sorted = df_clean.sort_values(by=['ticker', 'trade_date'])
    df_sorted['daily_return'] = df_sorted.groupby('ticker')['close_price'].pct_change()
    
    # Keep only relevant columns and drop NaNs (first day of each ticker)
    agg3 = df_sorted[['ticker', 'trade_date', 'daily_return']].dropna(subset=['daily_return'])
    agg3.to_parquet('agg3.parquet', index=False)
    print("Saved 'agg3.parquet' (simple daily return by ticker).")
    
    print("\nData processing and aggregation complete.")

if __name__ == "__main__":
    process_data('stock_market.csv')
