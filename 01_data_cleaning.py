import pandas as pd
import numpy as np
import re
from pathlib import Path


def convert_to_snake_case(column_name: str) -> str:
    """
    Convert column names to snake_case format.

    Args:
        column_name: Original column name

    Returns:
        Column name in snake_case format
    """
    # Remove leading/trailing whitespace
    column_name = column_name.strip()

    # Replace spaces with underscores
    column_name = column_name.replace(' ', '_')

    # Insert underscore before uppercase letters
    column_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', column_name)
    column_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', column_name)

    # Convert to lowercase
    column_name = column_name.lower()

    # Remove multiple underscores
    column_name = re.sub('_+', '_', column_name)

    # Remove leading/trailing underscores
    column_name = column_name.strip('_')

    return column_name


def standardize_null_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace various null representations with standard NaN values.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with standardized null values
    """
    null_representations = ['', 'NA', 'N/A', 'null', '-', 'nan', 'NaN', 'NULL', 'None']

    # Replace null representations with NaN for object columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].replace(null_representations, np.nan)
        df[col] = df[col].apply(lambda x: np.nan if isinstance(x, str) and x.strip() == '' else x)

    return df


def fix_date_format(date_str: str) -> str:
    """
    Convert various date formats to yyyy-MM-dd format.

    Args:
        date_str: Date string in various formats

    Returns:
        Date string in yyyy-MM-dd format
    """
    if pd.isna(date_str):
        return date_str

    # Remove leading/trailing whitespace
    date_str = str(date_str).strip()

    # Try multiple date formats
    date_formats = [
        '%Y/%m/%d',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y%m%d',
        '%m-%d-%Y',
        '%d-%m-%Y'
    ]

    for date_format in date_formats:
        try:
            date_obj = pd.to_datetime(date_str, format=date_format)
            return date_obj.strftime('%Y-%m-%d')
        except:
            continue

    # If no format matches, try pandas default parser
    try:
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime('%Y-%m-%d')
    except:
        return np.nan


def clean_data(input_file: str, output_file: str = 'cleaned.parquet') -> pd.DataFrame:
    """
    Main data cleaning function.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output Parquet file

    Returns:
        Cleaned DataFrame
    """
    print("Step 1: Loading raw data...")
    # Load raw data
    df = pd.read_csv(input_file)

    print(f"Raw data shape: {df.shape}")
    print(f"\nRaw columns: {df.columns.tolist()}")
    print(f"\nFirst 5 rows:")
    print(df.head())

    # Schema and null summary
    print("\n" + "="*80)
    print("RAW DATA SCHEMA AND NULL SUMMARY")
    print("="*80)
    print(df.info())
    print("\nNull values per column:")
    print(df.isnull().sum())

    print("\n" + "="*80)
    print("Step 2: Normalizing schema...")
    print("="*80)

    # Convert headers to snake_case
    df.columns = [convert_to_snake_case(col) for col in df.columns]
    print(f"Cleaned column names: {df.columns.tolist()}")

    # Trim whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Standardize text case (lowercase for consistency)
    for col in df.select_dtypes(include=['object']).columns:
        if col not in ['date']:  # Exclude date column
            df[col] = df[col].apply(lambda x: x.lower() if isinstance(x, str) else x)

    # Standardize null values
    df = standardize_null_values(df)

    print("\n" + "="*80)
    print("Step 3: Defining target schema and fixing data types...")
    print("="*80)

    # Fix date format if date column exists
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    if date_cols:
        date_col = date_cols[0]
        print(f"Fixing date format for column: {date_col}")
        df[date_col] = df[date_col].apply(fix_date_format)
        df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d', errors='coerce')

    # Define target schema based on column patterns
    for col in df.columns:
        if 'price' in col or 'open' in col or 'close' in col or 'high' in col or 'low' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif 'volume' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    print("\n" + "="*80)
    print("Step 4: Removing duplicates...")
    print("="*80)

    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    print(f"Duplicates removed: {duplicates_removed}")

    print("\n" + "="*80)
    print("CLEANED DATA SUMMARY")
    print("="*80)
    print(f"Cleaned data shape: {df.shape}")
    print(f"\nCleaned columns: {df.columns.tolist()}")
    print(df.info())
    print("\nNull values after cleaning:")
    print(df.isnull().sum())
    print("\nFirst 5 rows of cleaned data:")
    print(df.head())

    print("\n" + "="*80)
    print("Step 5: Saving to Parquet format...")
    print("="*80)

    # Save to parquet
    df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
    print(f"Data saved to: {output_file}")

    return df


if __name__ == "__main__":
    # Run the cleaning pipeline
    INPUT_FILE = "stock_market.csv"
    OUTPUT_FILE = "cleaned.parquet"

    try:
        cleaned_df = clean_data(INPUT_FILE, OUTPUT_FILE)
        print("\n✓ Data cleaning completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during data cleaning: {e}")
        raise