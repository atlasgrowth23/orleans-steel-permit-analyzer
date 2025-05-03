import pandas as pd
import numpy as np
import re
import io

def extract_lat_long(location_str):
    """
    Extract latitude and longitude from the 'Location 1' column string
    """
    if pd.isna(location_str):
        return None, None
        
    # Handle different formats of location strings
    try:
        # Try to extract coordinates using regex
        pattern = r"\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)"
        match = re.search(pattern, str(location_str))
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return lat, lng
        return None, None
    except:
        return None, None

def determine_potential_interest(row, materials_categories):
    """
    Determine the likely category of steel materials that might be of interest
    based on the permit description and other fields.
    """
    description = str(row.get('Description', '')).lower()
    permit_type = str(row.get('Type', '')).lower()
    
    # Initialize with a generic category for high-value projects
    if row.get('ConstrVal', 0) > 500000:
        return 'High Value Project'
    
    # Check for keywords related to specific materials categories
    for category, keywords in materials_categories.items():
        for keyword in keywords:
            if keyword in description:
                return category
    
    # Default category based on permit type
    if 'new construction' in permit_type:
        return 'Steel Framing'
    elif 'renovation' in permit_type and 'structural' in permit_type:
        return 'Steel Framing'
    elif 'roof' in description or 'roofing' in description:
        return 'Roofing'
    elif 'fence' in description or 'fencing' in description:
        return 'Fencing'
    elif 'gate' in description:
        return 'Gates'
    
    return 'Other'

def export_to_csv(df):
    """
    Export the DataFrame to a CSV string for download
    """
    # Create a buffer to hold the CSV data
    buffer = io.StringIO()
    
    # Export the DataFrame to CSV
    df.to_csv(buffer, index=False)
    
    # Get the string value
    csv_data = buffer.getvalue()
    
    return csv_data

def format_phone_number(phone):
    """
    Format a phone number for better readability
    """
    if pd.isna(phone):
        return ""
    
    phone_str = str(phone).strip()
    
    # Handle different formats
    if len(phone_str) == 10:
        return f"({phone_str[:3]}) {phone_str[3:6]}-{phone_str[6:]}"
    elif len(phone_str) == 7:
        return f"{phone_str[:3]}-{phone_str[3:]}"
    
    return phone_str

def format_address_for_map(address):
    """
    Format an address string to be used for mapping
    """
    if pd.isna(address):
        return ""
    
    # Add New Orleans, LA if not already present
    address_str = str(address).strip()
    if "new orleans" not in address_str.lower() and "la" not in address_str.lower():
        return f"{address_str}, New Orleans, LA"
    
    return address_str
