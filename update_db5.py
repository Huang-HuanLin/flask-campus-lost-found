from app import app, db

with app.app_context():
    # 添加评论模型支持寻物启事
    from sqlalchemy import text
    try:
        # SQL Server 语法
        db.session.execute(text('ALTER TABLE comment ADD notice_id INT'))
        db.session.commit()
        print("Added notice_id column to comment table")
    except Exception as e:
        print(f"Column may already exist: {e}")
    
    try:
        db.session.execute(text('ALTER TABLE notification ALTER COLUMN item_id INT NULL'))
        db.session.commit()
        print("Changed item_id in notification to allow NULL")
    except Exception as e:
        print(f"Column may already allow NULL: {e}")
    
    print("Database updated successfully!")
