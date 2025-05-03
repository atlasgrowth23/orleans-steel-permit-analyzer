import pandas as pd
import numpy as np
import re
import datetime
from utils import extract_lat_long

def load_and_clean_data(file):
    """
    Load CSV file into a pandas DataFrame and clean the data
    """
    try:
        # Load the data
        # Check if file is a string (file path) or file-like object
        if isinstance(file, str):
            df = pd.read_csv(file)
        else:
            df = pd.read_csv(file)
        
        # Check if the data is loaded correctly
        if df.empty:
            return None
            
        # Clean the data
        df = clean_data(df)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_data(df):
    """
    Clean and prepare the data for analysis
    """
    # Make a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Handle date fields
    date_fields = ['FilingDate', 'IssueDate', 'CurrentStatusDate', 'NextStatusDate']
    for field in date_fields:
        if field in df_clean.columns:
            try:
                df_clean[field] = pd.to_datetime(df_clean[field], errors='coerce')
            except:
                pass
                
    # Clean and convert numeric fields
    numeric_fields = ['ConstrVal', 'BldgArea', 'TotalFees', 'BondAmount']
    for field in numeric_fields:
        if field in df_clean.columns:
            # Remove non-numeric characters and convert to float
            df_clean[field] = pd.to_numeric(df_clean[field], errors='coerce')
            # Fill NaN values with 0
            df_clean[field] = df_clean[field].fillna(0)
            
    # Extract latitude and longitude from 'Location 1' column
    if 'Location 1' in df_clean.columns:
        # Extract lat/long for mapping
        df_clean['Latitude'], df_clean['Longitude'] = zip(*df_clean['Location 1'].apply(extract_lat_long))
        
    return df_clean

def filter_data(df, permit_type=None, category=None, start_date=None, end_date=None, min_value=0):
    """
    Filter the DataFrame based on multiple criteria
    """
    # Make a copy to avoid modifying the original
    filtered_df = df.copy()
    
    # Filter by permit type
    if permit_type:
        filtered_df = filtered_df[filtered_df['Type'] == permit_type]
        
    # Filter by category (which maps to keywords in description)
    if category:
        if category == 'Steel Framing':
            keywords = ['steel', 'frame', 'framing', 'metal', 'structure']
            filter_condition = filtered_df['Description'].str.contains('|'.join(keywords), case=False, na=False)
            filtered_df = filtered_df[filter_condition]
        elif category == 'Roofing':
            keywords = ['roof', 'r-panel', 'metal roof', 'paneling']
            filter_condition = filtered_df['Description'].str.contains('|'.join(keywords), case=False, na=False)
            filtered_df = filtered_df[filter_condition]
        elif category == 'Fencing':
            keywords = ['fence', 'fencing', 'fences', 'barrier', 'perimeter']
            filter_condition = filtered_df['Description'].str.contains('|'.join(keywords), case=False, na=False)
            filtered_df = filtered_df[filter_condition]
        elif category == 'Gates':
            keywords = ['gate', 'gates', 'entrance']
            filter_condition = filtered_df['Description'].str.contains('|'.join(keywords), case=False, na=False)
            filtered_df = filtered_df[filter_condition]
        elif category == 'Metal Materials':
            keywords = ['metal', 'steel', 'iron', 'aluminum']
            filter_condition = filtered_df['Description'].str.contains('|'.join(keywords), case=False, na=False)
            filtered_df = filtered_df[filter_condition]
        elif category == 'High Value Projects':
            filtered_df = filtered_df[filtered_df['ConstrVal'] > 250000]
    
    # Filter by date range
    if start_date and 'FilingDate' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['FilingDate'].dt.date >= start_date]
    if end_date and 'FilingDate' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['FilingDate'].dt.date <= end_date]
        
    # Filter by minimum construction value
    if min_value > 0 and 'ConstrVal' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ConstrVal'] >= min_value]
        
    return filtered_df

def calculate_statistics(df):
    """
    Calculate various statistics about the filtered data
    """
    stats = {}
    
    # Total number of permits
    stats["total_permits"] = len(df)
    
    # Total and average construction value
    if 'ConstrVal' in df.columns:
        stats["total_value"] = df['ConstrVal'].sum()
        stats["avg_value"] = df['ConstrVal'].mean() if len(df) > 0 else 0
        stats["high_value_count"] = len(df[df['ConstrVal'] > 250000])
    else:
        stats["total_value"] = 0
        stats["avg_value"] = 0
        stats["high_value_count"] = 0
        
    return stats
