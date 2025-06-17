import pandas as pd
import sqlite3
import os

def import_with_pandas(file_path, db_path, table_name):
    """
    Import data using pandas - handles various formats automatically
    """
    try:
        # Read file (try different delimiters)
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            # Try comma first, then tab delimiter
            try:
                df = pd.read_csv(file_path, delimiter=',')
            except:
                df = pd.read_csv(file_path, delimiter='\t')
        
        # Connect to SQLite and insert data
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"✓ Imported {len(df)} rows to {table_name}")
        
    except Exception as e:
        print(f"✗ Error importing {file_path}: {e}")

# Import all OtwartyWroclaw files
db_path = 'trips_populated.sqlite'

# List of typical GTFS files in OtwartyWroclaw dataset
gtfs_files = [
    ('calendar_dates.txt', 'calendar_dates'),
    ('routes.txt', 'routes'),
    ('stops.txt', 'stops'),
    ('stop_times.txt', 'stop_times'),
    ('trips.txt', 'trips'),
    ('shapes.txt', 'shapes'),
    ('agency.txt', 'agency'),
    ('calendar.txt', 'calendar'),
    ('fare_attributes.txt', 'fare_attributes'),
    ('fare_rules.txt', 'fare_rules')
]

print("Importing OtwartyWroclaw GTFS data...")
print("=" * 50)

for file_name, table_name in gtfs_files:
    if os.path.exists(file_name):
        import_with_pandas(file_name, db_path, table_name)
    else:
        print(f"⚠ File not found: {file_name}")

print("=" * 50)
print("Import completed!")

# Verify import by checking tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
conn.close()

print(f"\nTables created in {db_path}:")
for table in tables:
    print(f"  - {table[0]}")
