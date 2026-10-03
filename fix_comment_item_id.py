from app import app, db

with app.app_context():
    from sqlalchemy import text
    print("开始修复 comment 表的 item_id 字段...")
    
    try:
        db.session.execute(text('ALTER TABLE comment ALTER COLUMN item_id INT NULL'))
        db.session.commit()
        print("成功！comment 表的 item_id 字段已设为允许 NULL")
    except Exception as e:
        print(f"错误: {e}")
