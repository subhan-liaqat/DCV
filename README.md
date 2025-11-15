# Stock Market Analysis Dashboard

This project loads, cleans, and aggregates stock market data from a CSV (`stock_market.csv`) and displays it in an interactive Streamlit dashboard.

## Project Structure

-   `data_processing.py`: Python script to load raw CSV data, normalize and clean it, run aggregations, and save the results as `.parquet` files.
-   `app.py`: The Streamlit dashboard application that reads the `.parquet` files.
-   `requirements.txt`: Python dependencies.
-   `stock_market.csv`: The raw data file.
-   `cleaned.parquet`: (Generated) Cleaned, standardized data.
-   `agg1.parquet`: (Generated) Daily average close price by ticker.
-   `agg2.parquet`: (Generated) Average volume by sector.
-   `agg3.parquet`: (Generated) Simple daily return by ticker.

## Setup & Running

This project was developed using Python 3.10+. Using a virtual environment (like `uv`) is highly recommended.

### 1. Create and Activate Virtual Environment (using uv)

```bash
# Create a virtual environment in a .venv folder
uv venv

# Activate it
# On macOS/Linux
source .venv/bin/activate
# On Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

Install the required libraries from `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

### 3. Run the Data Processing Script

First, you must run this script to generate the `.parquet` data files that the app needs.

```bash
python data_processing.py
```

This will create `cleaned.parquet`, `agg1.parquet`, `agg2.parquet`, and `agg3.parquet` in your directory.

### 4. Run the Streamlit App

Once the data files are generated, you can run the dashboard:

```bash
streamlit run app.py
```

This will automatically open the interactive dashboard in your web browser.

## Streamlit Output Screenshots

*(You should add your 3-5 screenshots here after running the app)*

### Screenshot 1: Main Dashboard View
![Main dashboard showing all charts](your-image-path/screenshot1.png)

### Screenshot 2: Ticker Filter in Action
![Dashboard filtered for 'aapl' and 'msft'](your-image-path/screenshot2.png)

### Screenshot 3: Date Range Filter
![Dashboard showing a custom date range](your-image-path/screenshot3.png)
