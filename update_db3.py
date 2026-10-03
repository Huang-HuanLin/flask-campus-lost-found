import pyodbc

server = '吴锦浩\SQLSEVER'
database = 'lost_found'
username = 'sa'
password = 'Wjh18676509272_'

conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE lost_notice ADD contact_name VARCHAR(50)")
    print("Added contact_name column")
except Exception as e:
    print(f"contact_name column may already exist: {e}")

try:
    cursor.execute("ALTER TABLE lost_notice ADD contact_phone VARCHAR(20)")
    print("Added contact_phone column")
except Exception as e:
    print(f"contact_phone column may already exist: {e}")

conn.commit()
conn.close()
print("Database updated successfully!")