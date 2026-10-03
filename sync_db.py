from app import app, db, User, LostItem, LostNotice, Comment, Notification

with app.app_context():
    print("开始同步数据库...")
    
    # 创建所有表（如果不存在）
    db.create_all()
    print("所有表已创建")
    
    # 添加管理员用户（如果不存在）
    if not User.query.filter_by(username='admin').first():
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt(app)
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='admin', email='admin@example.com', password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print("管理员用户已创建")
    
    # 检查并添加comment表的notice_id字段
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    # 检查comment表
    comment_columns = [col['name'] for col in inspector.get_columns('comment')]
    if 'notice_id' not in comment_columns:
        from sqlalchemy import text
        db.session.execute(text('ALTER TABLE comment ADD notice_id INT'))
        db.session.commit()
        print("已添加 notice_id 字段到 comment 表")
    else:
        print("comment 表已包含 notice_id 字段")
    
    # 检查notification表的item_id是否允许NULL
    notification_columns = inspector.get_columns('notification')
    item_id_col = next((col for col in notification_columns if col['name'] == 'item_id'), None)
    if item_id_col and not item_id_col.get('nullable', False):
        from sqlalchemy import text
        db.session.execute(text('ALTER TABLE notification ALTER COLUMN item_id INT NULL'))
        db.session.commit()
        print("notification 表的 item_id 字段已设为允许 NULL")
    else:
        print("notification 表的 item_id 字段已允许 NULL")
    
    print("\n数据库同步完成！")
