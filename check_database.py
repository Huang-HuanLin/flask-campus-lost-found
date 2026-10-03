import pyodbc

# 连接数据库
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=吴锦浩\\SQLSEVER;'
    'DATABASE=lost_found;'
    'UID=sa;'
    'PWD=Wjh18676509272_'
)

cursor = conn.cursor()

# 查看所有表
print("=== 数据库表 ===")
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
for row in cursor.fetchall():
    print(row[0])

# 查看用户表
print("\n=== users 表数据 ===")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

# 查看失物表
print("\n=== lost_items 表数据 ===")
cursor.execute("SELECT * FROM lost_items")
for row in cursor.fetchall():
    print(row)

conn.close()
