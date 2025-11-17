# Quick Setup Guide

## Step-by-Step Instructions

### 1. Setup Environment

**Option A: Using UV (Recommended)**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project directory
mkdir stock-market-dashboard
cd stock-market-dashboard

# Initialize UV project
uv init

# Create pyproject.toml with dependencies
# (Copy the provided pyproject.toml content)

# Install dependencies
uv sync
```

**Option B: Using pip**
```bash
# Create project directory
mkdir stock-market-dashboard
cd stock-market-dashboard

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install pandas numpy pyarrow streamlit plotly requests
```

### 2. Download Data

```bash
# Download the CSV file
curl -O https://raw.githubusercontent.com/gchandra10/filestorage/refs/heads/main/stock_market.csv

# Or manually download and save as stock_market.csv
```

### 3. Copy Script Files

Create three Python files with the provided content:
- `01_data_cleaning.py`
- `02_create_aggregations.py`
- `03_streamlit_dashboard.py`

### 4. Run the Pipeline

```bash
# Step 1: Clean the data
python 01_data_cleaning.py

# Step 2: Create aggregations
python 02_create_aggregations.py

# Step 3: Launch dashboard
streamlit run 03_streamlit_dashboard.py
```

### 5. Take Screenshots

Open the dashboard at http://localhost:8501 and capture:
1. Main dashboard view with filters
2. Daily close prices chart
3. Volume by sector chart
4. Daily returns chart
5. Candlestick chart

Save screenshots in a `screenshots/` folder.

### 6. Create GitHub Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Stock market dashboard project"

# Create repository on GitHub and push
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 7. Submit

Submit your GitHub repository URL containing:
- All Python scripts
- README.md
- requirements.txt or pyproject.toml
- Screenshots (3-5 images)
- .gitignore

## Verification Checklist

- [ ] UV or pip environment setup
- [ ] All dependencies installed
- [ ] stock_market.csv downloaded
- [ ] cleaned.parquet generated
- [ ] Three aggregation parquet files created
- [ ] Streamlit dashboard runs successfully
- [ ] 3-5 screenshots captured
- [ ] README.md complete
- [ ] GitHub repository created
- [ ] All files committed and pushed

## Expected File Structure

```
stock-market-dashboard/
├── .git/
├── .venv/ (or managed by UV)
├── screenshots/
│   ├── 01_dashboard_overview.png
│   ├── 02_daily_close_prices.png
│   ├── 03_volume_by_sector.png
│   ├── 04_daily_returns.png
│   └── 05_candlestick.png
├── 01_data_cleaning.py
├── 02_create_aggregations.py
├── 03_streamlit_dashboard.py
├── stock_market.csv
├── cleaned.parquet
├── agg1_daily_avg_close.parquet
├── agg2_avg_volume_sector.parquet
├── agg3_daily_return.parquet
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```
