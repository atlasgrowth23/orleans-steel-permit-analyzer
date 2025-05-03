# Sample Data Files

This directory contains sample CSV data files for testing the Orleans Steel Permit Analyzer application.

## Available Samples:

- **New Orleans Permit Data (Last 7 Days)** - A sample of permit data from the City of New Orleans for the last 7 days.

## Data Structure

The permit data CSV files should contain the following fields:

- `Address`: Location of the permit/construction site
- `Owner`: Property owner name
- `Description`: Text description of the permitted work
- `Type`: Permit type (e.g., New Construction, Renovation, etc.)
- `FilingDate`: Date when the permit was filed
- `ConstrVal`: Construction value in dollars
- `BldgArea`: Building area in square feet
- `Location 1`: Lat/long coordinates for mapping

## Using Sample Data

To use these sample files with the application:

1. Start the application
2. Use the "Reload Default Data" button or upload one of these files manually

The application will automatically categorize permits based on their descriptions and values to identify potential leads for Orleans Steel Building Materials.
