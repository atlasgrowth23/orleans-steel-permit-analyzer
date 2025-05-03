import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
import re
import os
import datetime
from data_processing import load_and_clean_data, filter_data, calculate_statistics
from visualizations import create_map, create_bar_chart, create_pie_chart, create_time_series
from utils import extract_lat_long, determine_potential_interest, export_to_csv
from assets.orleans_steel_materials import materials_categories, product_descriptions
import database as db

# Set page config
st.set_page_config(
    page_title="Orleans Steel Permit Analyzer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("Orleans Steel Building Materials - Permit Analyzer")

# Create horizontal columns for description and images
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    This application helps analyze permit data from the City of New Orleans to identify potential clients 
    for Orleans Steel Building Materials. Filter permits by type, value, and keywords related to steel 
    building materials to discover new sales opportunities.
    """)

with col2:
    # Display a construction image
    st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", caption="Planning construction")

# Main content
st.markdown("---")

# Create three columns with images that represent Orleans Steel's product categories
col1, col2, col3 = st.columns(3)

with col1:
    st.image("https://images.unsplash.com/photo-1724814884427-9647e0b39fec", caption="Steel Framing")
    
with col2:
    st.image("https://images.unsplash.com/photo-1677945451878-de79f98149c9", caption="Metal Roofing")
    
with col3:
    st.image("https://images.unsplash.com/photo-1541888946425-d81bb19240f5", caption="Construction Projects")

# Data path - use sample data file from data_samples directory
data_path = "data_samples/sample_permit_data.csv"

# Database management section in sidebar
st.sidebar.title("Orleans Steel Permit Tool")
st.sidebar.markdown("---")
st.sidebar.header("Database Management")

# Upload a new CSV file option
new_csv_file = st.sidebar.file_uploader("Upload a new CSV file", type="csv")
if new_csv_file:
    if st.sidebar.button("Import New Data"):
        with st.spinner("Importing new data..."):
            success = db.import_csv_to_db(new_csv_file, materials_categories)
            if success:
                st.sidebar.success("New data imported successfully!")
                st.session_state['data_loaded'] = True
            else:
                st.sidebar.error("Failed to import new data.")

# Reload default data
if st.sidebar.button("Reload Default Data") or 'data_loaded' not in st.session_state:
    with st.spinner("Loading default data into database..."):
        success = db.import_csv_to_db(data_path, materials_categories)
        if success:
            st.sidebar.success("Default data loaded successfully!")
            st.session_state['data_loaded'] = True
        else:
            st.sidebar.error("Failed to load default data.")

# Get data from the database
df = db.get_permits_as_dataframe()

if df is not None and not df.empty:
    # Sidebar for filters
    st.sidebar.header("Filter Options")
    
    # Filter by permit type
    permit_types = ['All'] + sorted(df['Type'].unique().tolist())
    selected_permit_type = st.sidebar.selectbox("Select Permit Type", permit_types)
    
    # Filter by relevant categories for Orleans Steel
    interest_categories = ['All', 'Steel Framing', 'Roofing', 'Fencing', 'Gates', 'Metal Materials', 'High Value Projects']
    selected_category = st.sidebar.selectbox("Filter by Product Category", interest_categories)
    
    # Date filter
    if 'FilingDate' in df.columns:
        min_date = pd.to_datetime(df['FilingDate']).min().date()
        max_date = pd.to_datetime(df['FilingDate']).max().date()
        date_range = st.sidebar.date_input(
            "Filing Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = None, None
    
    # Minimum construction value
    if 'ConstrVal' in df.columns:
        max_value = int(df['ConstrVal'].max())
        if max_value > 0:
            min_value = st.sidebar.slider(
                "Minimum Construction Value ($)",
                min_value=0,
                max_value=max_value,
                value=0,
                step=10000
            )
        else:
            min_value = 0
    else:
        min_value = 0
    
    # Apply filters using the database
    filtered_df = db.filter_permits(
        permit_type=selected_permit_type if selected_permit_type != 'All' else None,
        category=selected_category if selected_category != 'All' else None,
        start_date=start_date,
        end_date=end_date,
        min_value=min_value
    )
    
    # Show statistics
    st.header("Filtered Permit Data")
    col1, col2, col3, col4 = st.columns(4)
    stats = calculate_statistics(filtered_df)
    
    col1.metric("Total Permits", stats["total_permits"])
    col2.metric("Total Construction Value", f"${stats['total_value']:,.0f}")
    col3.metric("Avg Construction Value", f"${stats['avg_value']:,.0f}")
    col4.metric("High Value Projects", stats["high_value_count"])
    
    # Display the filtered data
    st.markdown("### Permits")
    if not filtered_df.empty:
        # Add a "Potential Interest" column
        filtered_df['Potential Interest'] = filtered_df.apply(
            lambda row: determine_potential_interest(row, materials_categories),
            axis=1
        )
        
        # Display dataframe with key columns
        display_columns = ['Address', 'Description', 'Type', 'ConstrVal', 'BldgArea', 'FilingDate', 'Potential Interest']
        display_df = filtered_df[display_columns].copy()
        
        # Format construction value
        if 'ConstrVal' in display_df.columns:
            display_df['ConstrVal'] = display_df['ConstrVal'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
            
        # Rename columns for better display
        display_df.columns = ['Address', 'Description', 'Permit Type', 'Construction Value', 'Building Area (sqft)', 'Filing Date', 'Potential Interest']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Export button
        if st.button("Export Filtered Data to CSV"):
            csv_data = export_to_csv(filtered_df)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"orleans_steel_leads_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
        # Visualizations
        st.markdown("### Visualizations")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Map View", "Charts", "Summary"])
        
        with tab1:
            # Map of permit locations
            st.subheader("Permit Locations")
            map_fig = create_map(filtered_df)
            if map_fig:
                folium_static(map_fig, width=1000, height=600)
            else:
                st.info("No location data available for mapping. Check if the 'Location 1' column has valid coordinates.")
        
        with tab2:
            # Charts and graphs
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart of permit types
                if 'Type' in filtered_df.columns:
                    st.subheader("Permits by Type")
                    fig = create_bar_chart(filtered_df, 'Type', 'Permit Types', 'Number of Permits')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Time series of filing dates
                if 'FilingDate' in filtered_df.columns:
                    st.subheader("Permits by Filing Date")
                    fig = create_time_series(filtered_df)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Bar chart of potential interest categories
                st.subheader("Potential Interest Categories")
                fig = create_pie_chart(filtered_df, 'Potential Interest', 'Materials of Interest')
                st.plotly_chart(fig, use_container_width=True)
                
                # Construction value distribution
                if 'ConstrVal' in filtered_df.columns:
                    st.subheader("Construction Value Distribution")
                    fig = px.histogram(
                        filtered_df, 
                        x='ConstrVal',
                        nbins=20,
                        title='Distribution of Construction Values',
                        labels={'ConstrVal': 'Construction Value ($)'}
                    )
                    fig.update_layout(xaxis_title='Construction Value ($)', yaxis_title='Number of Permits')
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Summary statistics and insights
            st.subheader("Summary Statistics")
            
            # Create columns for different summary stats
            col1, col2 = st.columns(2)
            
            with col1:
                # Top contractors
                if 'Contractors' in filtered_df.columns:
                    contractor_counts = filtered_df['Contractors'].value_counts().reset_index()
                    contractor_counts.columns = ['Contractor', 'Number of Projects']
                    if not contractor_counts.empty and contractor_counts['Contractor'].iloc[0]:
                        st.write("Top Contractors:")
                        st.dataframe(contractor_counts.head(10), use_container_width=True)
                    else:
                        st.info("No contractor data available.")
            
            with col2:
                # Construction value by permit type
                if 'Type' in filtered_df.columns and 'ConstrVal' in filtered_df.columns:
                    value_by_type = filtered_df.groupby('Type')['ConstrVal'].sum().reset_index()
                    value_by_type.columns = ['Permit Type', 'Total Construction Value']
                    value_by_type['Total Construction Value'] = value_by_type['Total Construction Value'].apply(
                        lambda x: f"${x:,.0f}"
                    )
                    st.write("Construction Value by Permit Type:")
                    st.dataframe(value_by_type, use_container_width=True)
    else:
        st.info("No permits match the selected filters. Try adjusting your filter criteria.")
else:
    st.error("Unable to load data. Please check the database connection.")

# Footer information
st.markdown("---")
st.markdown("""
*Application developed for Orleans Steel Building Materials • Data sourced from the City of New Orleans permit database*
""")
