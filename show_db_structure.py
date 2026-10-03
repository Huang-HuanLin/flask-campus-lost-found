from app import app, db

with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    print("=" * 60)
    print("数据库表结构")
    print("=" * 60)
    
    # 获取所有表名
    tables = inspector.get_table_names()
    
    for table_name in tables:
        print(f"\n【表名】{table_name}")
        print("-" * 40)
        
        # 获取表的列信息
        columns = inspector.get_columns(table_name)
        
        print(f"{'字段名':<15} {'类型':<20} {'是否允许NULL':<10} {'主键':<6}")
        print("-" * 55)
        
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            nullable = '是' if col.get('nullable', False) else '否'
            primary_key = '是' if col.get('primary_key', False) else '否'
            
            print(f"{col_name:<15} {col_type:<20} {nullable:<10} {primary_key:<6}")
    
    print("\n" + "=" * 60)
