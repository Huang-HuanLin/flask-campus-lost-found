from app import app, db, Notification

with app.app_context():
    db.create_all()
    print("数据库表创建成功！")