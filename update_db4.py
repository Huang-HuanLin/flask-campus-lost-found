import pyodbc

server = '吴锦浩\SQLSEVER'
database = 'lost_found'
username = 'sa'
password = 'Wjh18676509272_'

conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE notification ALTER COLUMN item_id INT NULL")
    print("Changed item_id to allow NULL")
except Exception as e:
    print(f"Error: {e}")

conn.commit()
conn.close()
print("Database updated successfully!")