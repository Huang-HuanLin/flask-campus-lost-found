from app import app, db

with app.app_context():
    db.create_all()
    print("数据库表更新成功！")
    print("新增表：LostNotice, Comment, Favorite")