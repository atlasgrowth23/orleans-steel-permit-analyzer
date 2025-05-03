import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster

def create_map(df):
    """
    Create a folium map with markers for each permit location
    """
    # Check if we have latitude and longitude data
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        return None
        
    # Filter out rows with missing location data
    location_df = df.dropna(subset=['Latitude', 'Longitude'])
    
    if location_df.empty:
        return None
        
    # Create a map centered on New Orleans
    m = folium.Map(location=[29.9511, -90.0715], zoom_start=12)
    
    # Create a marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each location
    for idx, row in location_df.iterrows():
        # Create popup content
        popup_content = f"""
        <b>Address:</b> {row.get('Address', 'N/A')}<br>
        <b>Type:</b> {row.get('Type', 'N/A')}<br>
        <b>Value:</b> ${row.get('ConstrVal', 0):,.0f}<br>
        <b>Description:</b> {row.get('Description', 'N/A')}<br>
        """
        
        # Determine marker color based on construction value
        if 'ConstrVal' in row and row['ConstrVal'] > 500000:
            color = 'red'
        elif 'ConstrVal' in row and row['ConstrVal'] > 100000:
            color = 'orange'
        else:
            color = 'blue'
            
        # Create marker
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row.get('Address', 'Permit Location'),
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(marker_cluster)
        
    return m

def create_bar_chart(df, column, title, y_axis_title):
    """
    Create a bar chart based on the counts of values in a column
    """
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'count']
    
    # Sort by count in descending order
    value_counts = value_counts.sort_values('count', ascending=False)
    
    # Create the bar chart
    fig = px.bar(
        value_counts,
        x=column,
        y='count',
        title=title,
        labels={column: column, 'count': y_axis_title},
        color='count',
        color_continuous_scale='viridis'
    )
    
    return fig

def create_pie_chart(df, column, title):
    """
    Create a pie chart based on the counts of values in a column
    """
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'count']
    
    # Create the pie chart
    fig = px.pie(
        value_counts,
        names=column,
        values='count',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    return fig

def create_time_series(df):
    """
    Create a time series chart of permits by filing date
    """
    if 'FilingDate' not in df.columns:
        return None
        
    # Group by filing date and count
    date_counts = df.groupby(df['FilingDate'].dt.date).size().reset_index()
    date_counts.columns = ['FilingDate', 'count']
    
    # Create the time series chart
    fig = px.line(
        date_counts,
        x='FilingDate',
        y='count',
        title='Permits by Filing Date',
        labels={'FilingDate': 'Filing Date', 'count': 'Number of Permits'},
        markers=True
    )
    
    return fig
