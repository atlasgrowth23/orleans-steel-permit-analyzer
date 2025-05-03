# Orleans Steel Permit Analyzer - Setup Guide

This guide provides step-by-step instructions for setting up and running the Orleans Steel Permit Analyzer application.

## Requirements

- Python 3.8 or higher
- pip package manager

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/atlasgrowth23/orleans-steel-permit-analyzer.git
   cd orleans-steel-permit-analyzer
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit pandas numpy plotly folium streamlit-folium sqlalchemy
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

   This will start the application and open it in your default web browser. If it doesn't open automatically, you can access it at http://localhost:8501

## Data Configuration

The application expects permit data in CSV format. You can:

1. Use the default data file in `attached_assets/9 - last_7_days.csv` which loads automatically
2. Upload your own CSV file through the interface

The database will be created automatically in the `data` directory.

## Production Deployment

For production deployment, ensure you're using the configuration in `.streamlit/config.toml` which includes server settings for proper hosting:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## Troubleshooting

- **Database errors**: If you encounter database errors, try deleting the `data/permits.db` file and restarting the application to create a fresh database.
- **Data loading issues**: Ensure your CSV file has the required columns: Address, Description, Type, FilingDate, ConstrVal, etc.

## Contact

For support or questions, please open an issue on the GitHub repository.
