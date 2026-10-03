# 校园失物招领系统

一个基于 Flask 的校园失物招领管理系统，提供失物发布、认领、寻物启事、评论互动、通知提醒、管理员后台等完整功能，帮助校园内失主与拾得者快速建立联系。

## ✨ 功能特性

### 用户功能
- **注册 / 登录 / 登出**：基于 Flask-Login 的用户认证，密码使用 Bcrypt 加密存储
- **发布失物招领**：填写物品名称、分类、描述、发现地点、发现时间，支持上传图片（自动压缩至 800×800 以内）
- **浏览与搜索**：首页展示待认领物品，可按分类浏览，支持关键词（名称/描述/地点）+ 分类组合搜索
- **认领物品**：填写认领人姓名与联系方式，提交后通知发布者
- **确认领走 / 撤销认领**：发布者可确认物品已被领走，或在确认前撤销认领
- **寻物启事**：用户可发布寻物启事（丢失物品），其他用户可在下方评论提供线索
- **评论互动**：在招领物品和寻物启事下发表评论，发布者会收到通知
- **个人中心**：查看自己发布的招领与寻物启事，编辑个人信息（用户名、手机号、密码）
- **编辑 / 删除**：发布者可编辑或删除自己发布的物品
- **消息通知**：认领、评论等事件会生成站内通知，支持未读数角标

### 管理员功能
- **管理后台**：统一查看所有招领物品、寻物启事、用户列表
- **删除管理**：可删除任意招领记录或寻物启事（同时清理图片文件）
- **数据导出**：一键导出所有招领、寻物启事、用户数据为 CSV 文件

### 系统特性
- **物品分类**：证件、电子产品、书籍、衣物、水杯、其他
- **状态流转**：待认领（pending）→ 已认领（claimed）→ 已确认领走（confirmed）
- **自动清理**：物品确认领走 3 天后，由 APScheduler 定时任务自动删除数据及图片
- **统计信息**：首页展示各分类待认领数、总数、已确认数及认领率
- **响应式页面**：基于 Bootstrap 的响应式布局

## 🛠 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Python Flask 2.3 |
| ORM | Flask-SQLAlchemy 3.1 |
| 数据库 | Microsoft SQL Server（通过 pyodbc + ODBC Driver 17） |
| 认证 | Flask-Login 0.6 |
| 密码加密 | Flask-Bcrypt 1.0 |
| 图片处理 | Pillow 10.0 |
| 定时任务 | APScheduler 3.10 |
| 前端 | HTML + CSS + Bootstrap |
| 配置 | python-dotenv |

## 📋 环境要求

- Python 3.8+
- Microsoft SQL Server（需安装 **ODBC Driver 17 for SQL Server**）
- pip 包管理工具

## 🚀 安装与运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd web
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

1. 在 SQL Server 中创建数据库：

```sql
CREATE DATABASE lost_found;
```

2. 修改 [app.py](file:///d:/code/web/web/app.py#L13) 中的数据库连接字符串：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://用户名:密码@服务器名\\实例名/lost_found'
    '?driver=ODBC+Driver+17+for+SQL+Server'
)
```

> 也可在 [config.py](file:///d:/code/web/web/config.py) 中通过 `DATABASE_URL` 环境变量配置。

### 4. 创建上传目录

确保 `static/uploads` 目录存在（用于存放用户上传的图片）。

### 5. 初始化数据库

```bash
python init_db.py
```

该脚本会自动创建所有数据表，并创建默认管理员账号。

### 6. 启动应用

```bash
python app.py
```

访问 http://localhost:5000 即可进入系统。

> Windows 用户也可直接双击 `start.bat` 启动（注意修改其中的路径为你的实际项目路径）。

## 🔑 初始账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

普通用户需在注册页面自行注册。

## 📁 项目结构

```
web/
├── app.py                  # 主应用（路由、模型、定时任务）
├── config.py               # 配置文件
├── init_db.py              # 数据库初始化脚本
├── requirements.txt        # Python 依赖
├── setup.sql               # 数据库建表 SQL（参考）
├── start.bat               # Windows 启动脚本
├── static/
│   └── uploads/            # 用户上传的图片
└── templates/              # HTML 模板
    ├── index.html              # 首页（招领列表）
    ├── register.html           # 注册
    ├── login.html              # 登录
    ├── report.html             # 发布招领
    ├── item_detail.html        # 物品详情
    ├── item_edit.html          # 编辑物品
    ├── claim.html              # 认领物品
    ├── lost_notice_list.html   # 寻物启事列表
    ├── lost_notice_post.html   # 发布寻物启事
    ├── lost_notice_detail.html # 寻物启事详情
    ├── search_results.html     # 搜索结果
    ├── notifications.html      # 消息通知
    ├── profile.html            # 个人中心
    ├── profile_edit.html       # 编辑个人信息
    └── admin.html              # 管理后台
```

## 🗄 数据库表结构

### users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| username | varchar(100) | 用户名（唯一） |
| email | varchar(120) | 邮箱（唯一） |
| password | varchar(60) | 密码（Bcrypt 加密） |
| is_admin | boolean | 是否管理员 |
| phone | varchar(20) | 手机号 |
| created_at | datetime | 注册时间 |

### lost_items（失物招领表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | varchar(100) | 物品名称 |
| description | text | 物品描述 |
| category | varchar(50) | 分类 |
| location | varchar(100) | 发现地点 |
| found_time | datetime | 发现时间 |
| image_filename | varchar(200) | 图片文件名 |
| status | varchar(20) | 状态：pending / claimed / confirmed |
| reporter_id | int | 发布人 ID（外键） |
| claimer_name | varchar(100) | 认领人姓名 |
| claimer_phone | varchar(20) | 认领人电话 |
| claimed_at | datetime | 认领时间 |
| confirmed_at | datetime | 确认领走时间 |
| created_at | datetime | 创建时间 |

### lost_notices（寻物启事表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | varchar(100) | 丢失物品名称 |
| description | text | 描述 |
| category | varchar(50) | 分类 |
| location | varchar(100) | 丢失地点 |
| lost_time | datetime | 丢失时间 |
| image_filename | varchar(200) | 图片文件名 |
| contact_name | varchar(50) | 联系人 |
| contact_phone | varchar(20) | 联系电话 |
| status | varchar(20) | 状态：searching / found |
| user_id | int | 发布人 ID（外键） |
| created_at | datetime | 创建时间 |

### comments（评论表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| item_id | int | 关联招领物品 ID（可空） |
| notice_id | int | 关联寻物启事 ID（可空） |
| user_id | int | 评论人 ID（外键） |
| content | text | 评论内容 |
| created_at | datetime | 评论时间 |

### notifications（通知表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_id | int | 接收通知的用户 ID（外键） |
| item_id | int | 关联物品 ID（外键） |
| message | text | 通知内容 |
| read | boolean | 是否已读 |
| created_at | datetime | 创建时间 |

## ⚙️ 自动清理规则

- 物品状态变为「已确认领走」（confirmed）后，**3 天**自动删除该条记录及其图片
- 由 APScheduler 每 **24 小时**执行一次清理任务
- 管理员也可在后台手动删除任意记录

## ⚠️ 注意事项

1. 确保 SQL Server 服务正常运行，且已安装 ODBC Driver 17
2. `static/uploads` 目录需具备写入权限
3. 生产环境务必修改 `app.py` 中的 `SECRET_KEY`
4. 自动清理任务需保持应用进程运行才能生效
5. 图片上传大小限制为 16MB

## 📄 License

MIT License
