from app import app, db

with app.app_context():
    # 添加寻物启事的联系方式字段
    try:
        db.engine.execute('ALTER TABLE lost_notice ADD COLUMN contact_name VARCHAR(50)')
        print("Added contact_name column")
    except Exception as e:
        print(f"contact_name column may already exist: {e}")
    
    try:
        db.engine.execute('ALTER TABLE lost_notice ADD COLUMN contact_phone VARCHAR(20)')
        print("Added contact_phone column")
    except Exception as e:
        print(f"contact_phone column may already exist: {e}")

print("Database updated successfully!")