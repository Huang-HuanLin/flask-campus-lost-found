import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here_change_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:Wjh18676509272_@吴锦浩\\SQLSEVER/lost_found?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    found_time = db.Column(db.DateTime)
    image_filename = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    claimer_name = db.Column(db.String(100))
    claimer_phone = db.Column(db.String(20))
    claimed_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reporter = db.relationship('User', backref=db.backref('reported_items', lazy=True))
    
    def __repr__(self):
        return f"LostItem('{self.name}', '{self.category}', '{self.status}')"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    item = db.relationship('LostItem', backref=db.backref('notifications', lazy=True))
    
    def __repr__(self):
        return f"Notification('{self.user_id}', '{self.item_id}', '{self.read}')"

# 寻物启事模型
class LostNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    lost_time = db.Column(db.DateTime)
    image_filename = db.Column(db.String(200))
    contact_name = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='searching')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('lost_notices', lazy=True))
    
    def __repr__(self):
        return f"LostNotice('{self.name}', '{self.category}', '{self.status}')"

# 评论模型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'))
    notice_id = db.Column(db.Integer, db.ForeignKey('lost_notice.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    item = db.relationship('LostItem', backref=db.backref('comments', lazy=True))
    notice = db.relationship('LostNotice', backref=db.backref('comments', lazy=True))
    
    def __repr__(self):
        return f"Comment('{self.user_id}', '{self.item_id}', '{self.notice_id}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    items = LostItem.query.filter_by(status='pending').order_by(LostItem.created_at.desc()).all()
    categories = ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']
    return render_template('index.html', items=items, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password, phone=phone)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('登录失败，请检查邮箱和密码', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_image(image):
    random_name = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    
    img = Image.open(image)
    img.thumbnail((800, 800))
    img.save(image_path)
    
    return random_name

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    categories = ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')
        category = request.form['category']
        location = request.form['location']
        found_time = request.form['found_time']
        
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_filename = save_image(image)
        
        item = LostItem(
            name=name,
            description=description,
            category=category,
            location=location,
            found_time=datetime.strptime(found_time.replace('T', ' '), '%Y-%m-%d %H:%M'),
            image_filename=image_filename,
            reporter_id=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('失物招领信息已发布', 'success')
        return redirect(url_for('index'))
    
    return render_template('report.html', categories=categories)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = LostItem.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@app.route('/claim/<int:item_id>', methods=['GET', 'POST'])
@login_required
def claim(item_id):
    item = LostItem.query.get_or_404(item_id)
    
    if item.status != 'pending':
        flash('该物品已被认领', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))
    
    if request.method == 'POST':
        item.claimer_name = request.form['claimer_name']
        item.claimer_phone = request.form['claimer_phone']
        item.status = 'claimed'
        item.claimed_at = datetime.utcnow()
        
        notification = Notification(
            user_id=item.reporter_id,
            item_id=item.id,
            message=f'您发布的「{item.name}」已被 {request.form["claimer_name"]} 认领，请及时确认'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('认领申请已提交，请等待物品所有人确认', 'success')
        return redirect(url_for('item_detail', item_id=item_id))
    
    return render_template('claim.html', item=item)

@app.route('/confirm/<int:item_id>')
@login_required
def confirm(item_id):
    item = LostItem.query.get_or_404(item_id)
    
    if item.reporter_id != current_user.id and not current_user.is_admin:
        flash('您无权确认此物品', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))
    
    if item.status != 'claimed':
        flash('该物品状态不允许确认', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))
    
    item.status = 'confirmed'
    item.confirmed_at = datetime.utcnow()
    db.session.commit()
    
    flash('物品已确认领走', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/cancel_claim/<int:item_id>')
@login_required
def cancel_claim(item_id):
    item = LostItem.query.get_or_404(item_id)
    
    if item.status != 'claimed':
        flash('该物品当前状态不允许撤销认领', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))
    
    item.status = 'pending'
    item.claimer_name = None
    item.claimer_phone = None
    item.claimed_at = None
    db.session.commit()
    
    flash('认领已撤销，物品重新开放认领', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for notification in notifications:
        notification.read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)

@app.route('/mark_notification_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.read = True
        db.session.commit()
    return redirect(url_for('notifications'))

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
        return dict(unread_count=unread_count)
    return {}

@app.route('/category/<string:category>')
def category(category):
    items = LostItem.query.filter_by(category=category, status='pending').order_by(LostItem.created_at.desc()).all()
    categories = ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']
    return render_template('index.html', items=items, categories=categories, active_category=category)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('您不是管理员', 'danger')
        return redirect(url_for('index'))
    
    items = LostItem.query.order_by(LostItem.created_at.desc()).all()
    notices = LostNotice.query.order_by(LostNotice.created_at.desc()).all()
    users = User.query.all()
    return render_template('admin.html', items=items, notices=notices, users=users)

@app.route('/admin/delete/<int:item_id>')
@login_required
def admin_delete(item_id):
    if not current_user.is_admin:
        flash('您不是管理员', 'danger')
        return redirect(url_for('index'))
    
    item = LostItem.query.get_or_404(item_id)
    
    if item.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(item)
    db.session.commit()
    
    flash('物品已删除', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/notice/delete/<int:notice_id>')
@login_required
def admin_notice_delete(notice_id):
    if not current_user.is_admin:
        flash('您不是管理员', 'danger')
        return redirect(url_for('index'))
    
    notice = LostNotice.query.get_or_404(notice_id)
    
    if notice.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], notice.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(notice)
    db.session.commit()
    
    flash('寻物启事已删除', 'success')
    return redirect(url_for('admin'))

def auto_cleanup():
    with app.app_context():
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        items_to_delete = LostItem.query.filter(
            LostItem.status == 'confirmed',
            LostItem.confirmed_at <= three_days_ago
        ).all()
        
        for item in items_to_delete:
            if item.image_filename:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            db.session.delete(item)
        
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(auto_cleanup, 'interval', hours=24)
scheduler.start()

@app.context_processor
def inject_categories():
    return dict(categories=['证件', '电子产品', '书籍', '衣物', '水杯', '其他'])

# ========== 功能1: 用户个人中心 ==========
@app.route('/profile')
@login_required
def profile():
    my_items = LostItem.query.filter_by(reporter_id=current_user.id).order_by(LostItem.created_at.desc()).all()
    my_notices = LostNotice.query.filter_by(user_id=current_user.id).order_by(LostNotice.created_at.desc()).all()
    return render_template('profile.html', my_items=my_items, my_notices=my_notices)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.phone = request.form.get('phone')
        if request.form.get('password'):
            current_user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        db.session.commit()
        flash('个人信息已更新', 'success')
        return redirect(url_for('profile'))
    return render_template('profile_edit.html')

# ========== 功能2: 搜索功能 ==========
@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    
    items = LostItem.query.filter(LostItem.status == 'pending')
    
    if keyword:
        items = items.filter(
            db.or_(
                LostItem.name.contains(keyword),
                LostItem.description.contains(keyword),
                LostItem.location.contains(keyword)
            )
        )
    
    if category:
        items = items.filter_by(category=category)
    
    items = items.order_by(LostItem.created_at.desc()).all()
    categories = ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']
    return render_template('search_results.html', items=items, keyword=keyword, categories=categories)

# ========== 功能3: 寻物启事功能 ==========
@app.route('/lost_notice')
def lost_notice_list():
    notices = LostNotice.query.filter_by(status='searching').order_by(LostNotice.created_at.desc()).all()
    return render_template('lost_notice_list.html', notices=notices)

@app.route('/lost_notice/post', methods=['GET', 'POST'])
@login_required
def lost_notice_post():
    categories = ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')
        category = request.form['category']
        location = request.form['location']
        lost_time = request.form['lost_time']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_filename = save_image(image)
        
        notice = LostNotice(
            name=name,
            description=description,
            category=category,
            location=location,
            lost_time=datetime.strptime(lost_time.replace('T', ' '), '%Y-%m-%d %H:%M'),
            image_filename=image_filename,
            contact_name=contact_name,
            contact_phone=contact_phone,
            user_id=current_user.id
        )
        
        db.session.add(notice)
        db.session.commit()
        
        flash('寻物启事已发布', 'success')
        return redirect(url_for('lost_notice_list'))
    
    return render_template('lost_notice_post.html', categories=categories)

@app.route('/lost_notice/<int:notice_id>')
def lost_notice_detail(notice_id):
    notice = LostNotice.query.get_or_404(notice_id)
    comments = Comment.query.filter_by(notice_id=notice_id).order_by(Comment.created_at.desc()).all()
    return render_template('lost_notice_detail.html', notice=notice, comments=comments)

@app.route('/lost_notice/comment/<int:notice_id>', methods=['POST'])
@login_required
def lost_notice_comment(notice_id):
    notice = LostNotice.query.get_or_404(notice_id)
    
    content = request.form['content']
    
    comment = Comment(
        notice_id=notice_id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(comment)
    
    # 给发布者发送通知
    notification = Notification(
        user_id=notice.user_id,
        message=f"有人在您发布的「{notice.name}」寻物启事中发表了评论：{content}"
    )
    db.session.add(notification)
    
    db.session.commit()
    
    flash('评论已发布', 'success')
    return redirect(url_for('lost_notice_detail', notice_id=notice_id))

@app.route('/lost_notice/found/<int:notice_id>')
@login_required
def lost_notice_found(notice_id):
    notice = LostNotice.query.get_or_404(notice_id)
    if notice.user_id != current_user.id and not current_user.is_admin:
        flash('您无权操作', 'danger')
        return redirect(url_for('lost_notice_list'))
    notice.status = 'found'
    db.session.commit()
    flash('已标记为找到', 'success')
    return redirect(url_for('lost_notice_list'))

# ========== 功能4: 物品编辑功能 ==========
@app.route('/item/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item_edit(item_id):
    item = LostItem.query.get_or_404(item_id)
    
    if item.reporter_id != current_user.id and not current_user.is_admin:
        flash('您无权编辑此物品', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))
    
    categories = ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form.get('description')
        item.category = request.form['category']
        item.location = request.form['location']
        item.found_time = datetime.strptime(request.form['found_time'].replace('T', ' '), '%Y-%m-%d %H:%M')
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                if item.image_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                item.image_filename = save_image(image)
        
        db.session.commit()
        flash('物品信息已更新', 'success')
        return redirect(url_for('item_detail', item_id=item_id))
    
    return render_template('item_edit.html', item=item, categories=categories)

@app.route('/item/delete/<int:item_id>')
@login_required
def item_delete(item_id):
    item = LostItem.query.get_or_404(item_id)
    
    if item.reporter_id != current_user.id and not current_user.is_admin:
        flash('您无权删除此物品', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))
    
    if item.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(item)
    db.session.commit()
    
    flash('物品已删除', 'success')
    return redirect(url_for('profile'))

# ========== 功能5: 物品统计 ==========
@app.context_processor
def inject_stats():
    pending_items = LostItem.query.filter_by(status='pending').count()
    confirmed_items = LostItem.query.filter_by(status='confirmed').count()
    lost_notice_count = LostNotice.query.filter_by(status='searching').count()
    
    category_stats = {}
    for cat in ['证件', '电子产品', '书籍', '衣物', '水杯', '其他']:
        cat_pending = LostItem.query.filter_by(category=cat, status='pending').count()
        cat_total = LostItem.query.filter_by(category=cat).count()
        cat_confirmed = LostItem.query.filter_by(category=cat, status='confirmed').count()
        category_stats[cat] = {
            'pending': cat_pending,
            'total': cat_total,
            'confirmed': cat_confirmed,
            'rate': round(cat_confirmed / cat_total * 100 if cat_total > 0 else 0, 1)
        }
    
    return dict(pending_items=pending_items, confirmed_items=confirmed_items, lost_notice_count=lost_notice_count, category_stats=category_stats)

# ========== 功能6: 评论/留言功能 ==========
@app.route('/item/<int:item_id>/comment', methods=['POST'])
@login_required
def add_comment(item_id):
    item = LostItem.query.get_or_404(item_id)
    content = request.form['content']
    
    if not content:
        flash('评论内容不能为空', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))
    
    comment = Comment(item_id=item_id, user_id=current_user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    
    flash('评论已发布', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/comment/delete/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('您无权删除此评论', 'danger')
        return redirect(url_for('item_detail', item_id=comment.item_id))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('评论已删除', 'success')
    return redirect(url_for('item_detail', item_id=comment.item_id))

# ========== 功能7: 数据导出功能 ==========
@app.route('/admin/export')
@login_required
def admin_export():
    if not current_user.is_admin:
        flash('您不是管理员', 'danger')
        return redirect(url_for('index'))
    
    import io
    import csv
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 物品招领数据
    writer.writerow(['物品招领数据'])
    writer.writerow(['ID', '物品名称', '分类', '地点', '发现时间', '状态', '发布人', '认领人', '认领电话', '发布时间'])
    
    items = LostItem.query.order_by(LostItem.created_at.desc()).all()
    for item in items:
        writer.writerow([
            item.id,
            item.name,
            item.category,
            item.location,
            item.found_time.strftime('%Y/%m/%d %H:%M') if item.found_time else '',
            item.status,
            item.reporter.username,
            item.claimer_name or '',
            item.claimer_phone or '',
            item.created_at.strftime('%Y/%m/%d %H:%M')
        ])
    
    # 寻物启事数据
    writer.writerow([''])
    writer.writerow(['寻物启事数据'])
    writer.writerow(['ID', '物品名称', '分类', '丢失地点', '丢失时间', '状态', '发布人', '联系人', '联系电话', '发布时间'])
    
    notices = LostNotice.query.order_by(LostNotice.created_at.desc()).all()
    for notice in notices:
        writer.writerow([
            notice.id,
            notice.name,
            notice.category,
            notice.location,
            notice.lost_time.strftime('%Y/%m/%d %H:%M') if notice.lost_time else '',
            notice.status,
            notice.user.username,
            notice.contact_name or '',
            notice.contact_phone or '',
            notice.created_at.strftime('%Y/%m/%d %H:%M')
        ])
    
    # 用户数据
    writer.writerow([''])
    writer.writerow(['用户数据'])
    writer.writerow(['ID', '用户名', '邮箱', '手机号', '角色', '注册时间'])
    
    users = User.query.all()
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.phone or '',
            '管理员' if user.is_admin else '普通用户',
            user.created_at.strftime('%Y/%m/%d %H:%M')
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=lost_found_data.csv'}
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(username='admin', email='admin@example.com', password=hashed_password, is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
    
    app.run(debug=True)
