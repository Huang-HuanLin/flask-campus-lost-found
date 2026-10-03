from app import app, db, User, bcrypt

with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password=hashed_password,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("管理员账号已创建: admin / admin123")
    
    print("数据库初始化完成")
