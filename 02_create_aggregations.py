import pandas as pd
import numpy as np
from pathlib import Path


def create_daily_avg_close_by_ticker(df: pd.DataFrame, output_file: str = 'agg1_daily_avg_close.parquet') -> pd.DataFrame:
    """
    Create aggregation 1: Daily average close price by ticker.

    Args:
        df: Cleaned DataFrame
        output_file: Output file path

    Returns:
        Aggregated DataFrame
    """
    print("Creating Aggregation 1: Daily Average Close by Ticker...")

    # Identify date and ticker columns dynamically
    date_col = [col for col in df.columns if 'date' in col.lower()][0]
    ticker_col = [col for col in df.columns if 'ticker' in col.lower()][0]
    close_col = [col for col in df.columns if 'close' in col.lower()][0]

    # Create aggregation
    agg_df = df.groupby([date_col, ticker_col]).agg({
        close_col: ['mean', 'min', 'max', 'count']
    }).reset_index()

    # Flatten column names
    agg_df.columns = [f'{col[0]}_{col[1]}' if col[1] else col[0] for col in agg_df.columns]

    # Rename columns for clarity
    agg_df.columns = [date_col, ticker_col, 'avg_close_price', 'min_close_price', 'max_close_price', 'record_count']

    print(f"Aggregation 1 shape: {agg_df.shape}")
    print(f"Sample data:\n{agg_df.head()}")

    # Save to parquet
    agg_df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
    print(f"Saved to: {output_file}\n")

    return agg_df


def create_avg_volume_by_sector(df: pd.DataFrame, output_file: str = 'agg2_avg_volume_sector.parquet') -> pd.DataFrame:
    """
    Create aggregation 2: Average volume by sector.

    Args:
        df: Cleaned DataFrame
        output_file: Output file path

    Returns:
        Aggregated DataFrame
    """
    print("Creating Aggregation 2: Average Volume by Sector...")

    # Identify sector and volume columns dynamically
    sector_col = [col for col in df.columns if 'sector' in col.lower()]
    volume_col = [col for col in df.columns if 'volume' in col.lower()][0]

    if not sector_col:
        print("Warning: No sector column found. Skipping this aggregation.")
        return None

    sector_col = sector_col[0]

    # Create aggregation
    agg_df = df.groupby(sector_col).agg({
        volume_col: ['mean', 'median', 'sum', 'count']
    }).reset_index()

    # Flatten column names
    agg_df.columns = [sector_col, 'avg_volume', 'median_volume', 'total_volume', 'record_count']

    # Sort by average volume
    agg_df = agg_df.sort_values('avg_volume', ascending=False)

    print(f"Aggregation 2 shape: {agg_df.shape}")
    print(f"Sample data:\n{agg_df}")

    # Save to parquet
    agg_df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
    print(f"Saved to: {output_file}\n")

    return agg_df


def create_daily_return_by_ticker(df: pd.DataFrame, output_file: str = 'agg3_daily_return.parquet') -> pd.DataFrame:
    """
    Create aggregation 3: Simple daily return by ticker.
    Daily Return = (Close - Open) / Open * 100

    Args:
        df: Cleaned DataFrame
        output_file: Output file path

    Returns:
        Aggregated DataFrame
    """
    print("Creating Aggregation 3: Daily Return by Ticker...")

    # Identify required columns dynamically
    date_col = [col for col in df.columns if 'date' in col.lower()][0]
    ticker_col = [col for col in df.columns if 'ticker' in col.lower()][0]
    open_col = [col for col in df.columns if 'open' in col.lower() and 'price' in col.lower()][0]
    close_col = [col for col in df.columns if 'close' in col.lower() and 'price' in col.lower()][0]

    # Calculate daily return
    df_copy = df.copy()
    df_copy['daily_return_pct'] = ((df_copy[close_col] - df_copy[open_col]) / df_copy[open_col] * 100).round(2)

    # Create aggregation with return statistics
    agg_df = df_copy.groupby([date_col, ticker_col]).agg({
        'daily_return_pct': ['mean', 'min', 'max'],
        open_col: 'first',
        close_col: 'last'
    }).reset_index()

    # Flatten column names
    agg_df.columns = [date_col, ticker_col, 'avg_daily_return_pct', 'min_daily_return_pct', 
                      'max_daily_return_pct', 'open_price', 'close_price']

    print(f"Aggregation 3 shape: {agg_df.shape}")
    print(f"Sample data:\n{agg_df.head()}")

    # Save to parquet
    agg_df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
    print(f"Saved to: {output_file}\n")

    return agg_df


def create_aggregations(input_file: str = 'cleaned.parquet'):
    """
    Main function to create all aggregations.

    Args:
        input_file: Path to cleaned parquet file
    """
    print("="*80)
    print("LOADING CLEANED DATA")
    print("="*80)

    # Load cleaned data
    df = pd.read_parquet(input_file)

    print(f"Loaded data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nData preview:")
    print(df.head())

    print("\n" + "="*80)
    print("CREATING AGGREGATIONS")
    print("="*80 + "\n")

    # Create all aggregations
    agg1 = create_daily_avg_close_by_ticker(df)
    agg2 = create_avg_volume_by_sector(df)
    agg3 = create_daily_return_by_ticker(df)

    return agg1, agg2, agg3


if __name__ == "__main__":
    INPUT_FILE = "cleaned.parquet"

    try:
        agg1, agg2, agg3 = create_aggregations(INPUT_FILE)
        print("="*80)
        print("✓ All aggregations created successfully!")
        print("="*80)
    except Exception as e:
        print(f"\n✗ Error during aggregation creation: {e}")
        raise