import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database path
DATABASE_URL = 'sqlite:///data/orleans_permits.db'

# Create directory for the database if it doesn't exist
os.makedirs('data', exist_ok=True)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for the models
Base = declarative_base()

# Define the Permit class that maps to the permits table
class Permit(Base):
    __tablename__ = 'permits'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    owner = Column(String(255))
    description = Column(Text)
    num_string = Column(String(50))
    is_closed = Column(Boolean)
    type = Column(String(100))
    code = Column(String(20))
    filing_date = Column(DateTime)
    issue_date = Column(DateTime)
    current_status = Column(String(100))
    land_use = Column(String(100))
    land_use_short = Column(String(20))
    project_name = Column(String(255))
    building_area = Column(Float)
    construction_value = Column(Float)
    applicant = Column(String(255))
    contractors = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    potential_interest = Column(String(100))
    
    def __repr__(self):
        return f"<Permit(id={self.id}, address='{self.address}', type='{self.type}')>"

# Create the tables
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Get a database session
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def import_csv_to_db(csv_file, materials_categories):
    """
    Import CSV data into the database
    """
    from data_processing import load_and_clean_data
    from utils import extract_lat_long, determine_potential_interest
    
    # Load the CSV file
    df = load_and_clean_data(csv_file)
    
    if df is None or df.empty:
        return False
    
    # Add potential interest column
    df['Potential Interest'] = df.apply(
        lambda row: determine_potential_interest(row, materials_categories),
        axis=1
    )
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # First, delete all existing permits
        db.query(Permit).delete()
        
        # Prepare the data for database insertion
        permits_to_add = []
        for _, row in df.iterrows():
            # Extract latitude and longitude if not already present
            if 'Latitude' not in row and 'Longitude' not in row and 'Location 1' in row:
                lat, lng = extract_lat_long(row['Location 1'])
            else:
                lat = row.get('Latitude')
                lng = row.get('Longitude')
            
            # Create a permit object
            permit = Permit(
                address=row.get('Address', ''),
                owner=row.get('Owner', ''),
                description=row.get('Description', ''),
                num_string=row.get('NumString', ''),
                is_closed=row.get('IsClosed', False),
                type=row.get('Type', ''),
                code=row.get('Code', ''),
                filing_date=row.get('FilingDate'),
                issue_date=row.get('IssueDate'),
                current_status=row.get('CurrentStatus', ''),
                land_use=row.get('LandUse', ''),
                land_use_short=row.get('LandUseShort', ''),
                project_name=row.get('ProjectName', ''),
                building_area=row.get('BldgArea', 0),
                construction_value=row.get('ConstrVal', 0),
                applicant=row.get('Applicant', ''),
                contractors=row.get('Contractors', ''),
                latitude=lat,
                longitude=lng,
                potential_interest=row.get('Potential Interest', '')
            )
            permits_to_add.append(permit)
        
        # Add the permits to the database
        db.add_all(permits_to_add)
        db.commit()
        
        return True
    except Exception as e:
        print(f"Error importing data to database: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_all_permits():
    """
    Get all permits from the database
    """
    db = SessionLocal()
    try:
        permits = db.query(Permit).all()
        return permits
    finally:
        db.close()
        
def get_permits_as_dataframe():
    """
    Get all permits from the database as a pandas DataFrame
    """
    db = SessionLocal()
    try:
        # Get all permits
        permits = db.query(Permit).all()
        
        # Convert to DataFrame
        permit_data = [{
            'Address': p.address,
            'Owner': p.owner,
            'Description': p.description,
            'NumString': p.num_string,
            'IsClosed': p.is_closed,
            'Type': p.type,
            'Code': p.code,
            'FilingDate': p.filing_date,
            'IssueDate': p.issue_date,
            'CurrentStatus': p.current_status,
            'LandUse': p.land_use,
            'LandUseShort': p.land_use_short,
            'ProjectName': p.project_name,
            'BldgArea': p.building_area,
            'ConstrVal': p.construction_value,
            'Applicant': p.applicant,
            'Contractors': p.contractors,
            'Latitude': p.latitude,
            'Longitude': p.longitude,
            'Potential Interest': p.potential_interest
        } for p in permits]
        
        df = pd.DataFrame(permit_data)
        return df
    finally:
        db.close()

def filter_permits(permit_type=None, category=None, start_date=None, end_date=None, min_value=0):
    """
    Filter permits based on criteria and return as DataFrame
    """
    db = SessionLocal()
    try:
        # Start with a base query
        query = db.query(Permit)
        
        # Apply filters
        if permit_type:
            query = query.filter(Permit.type == permit_type)
            
        if category:
            if category == 'High Value Projects':
                query = query.filter(Permit.construction_value > 250000)
            else:
                query = query.filter(Permit.potential_interest == category)
        
        if start_date:
            query = query.filter(Permit.filing_date >= start_date)
            
        if end_date:
            query = query.filter(Permit.filing_date <= end_date)
            
        if min_value > 0:
            query = query.filter(Permit.construction_value >= min_value)
        
        # Execute the query
        permits = query.all()
        
        # Convert to DataFrame
        permit_data = [{
            'Address': p.address,
            'Owner': p.owner,
            'Description': p.description,
            'NumString': p.num_string,
            'IsClosed': p.is_closed,
            'Type': p.type,
            'Code': p.code,
            'FilingDate': p.filing_date,
            'IssueDate': p.issue_date,
            'CurrentStatus': p.current_status,
            'LandUse': p.land_use,
            'LandUseShort': p.land_use_short,
            'ProjectName': p.project_name,
            'BldgArea': p.building_area,
            'ConstrVal': p.construction_value,
            'Applicant': p.applicant,
            'Contractors': p.contractors,
            'Latitude': p.latitude,
            'Longitude': p.longitude,
            'Potential Interest': p.potential_interest
        } for p in permits]
        
        df = pd.DataFrame(permit_data)
        return df
    finally:
        db.close()
