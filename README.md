# 校园失物招领网站

基于 Flask + MySQL 的校园失物招领管理系统，支持用户注册登录、发布招领信息、物品认领、管理员管理等功能。

## 功能特性

### 用户功能
- 用户注册/登录
- 发布失物招领（支持图片上传）
- 按分类浏览物品
- 认领物品（填写联系方式）
- 确认物品领走

### 管理员功能
- 专属管理后台
- 审核管理所有招领信息
- 删除任意招领记录
- 查看所有用户和认领记录

### 核心特性
- 失物分类：证件、电子产品、书籍、衣物、水杯、其他
- 状态流转：待认领 → 已有人认领 → 确认领走
- 自动清理：物品确认领走后3天自动删除
- 图片上传与管理
- 响应式页面设计

## 技术栈

- **后端**: Python Flask
- **前端**: HTML + CSS + Bootstrap
- **数据库**: MySQL 8.0
- **图片处理**: Pillow
- **定时任务**: APScheduler
- **密码加密**: Flask-Bcrypt

## 环境要求

- Python 3.8+
- MySQL 8.0+
- pip 包管理工具

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd campus-lost-found
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

1. 创建 MySQL 数据库：
```sql
CREATE DATABASE lost_found CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改数据库连接配置（在 `app.py` 或环境变量中）：
```python
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://username:password@localhost/lost_found'
```

### 4. 创建必要目录

```bash
mkdir -p static/uploads
```

### 5. 初始化数据库

```bash
python init_db.py
```

### 6. 运行应用

```bash
python app.py
```

访问 http://localhost:5000 即可进入网站。

## 初始账号

- **管理员账号**: admin / admin123
- 普通用户需自行注册

## 项目结构

```
campus-lost-found/
├── app.py              # 主应用文件
├── config.py           # 配置文件
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # 依赖列表
├── README.md           # 项目说明
├── static/
│   └── uploads/        # 图片上传目录
└── templates/          # HTML模板
    ├── index.html      # 首页
    ├── login.html      # 登录页
    ├── register.html   # 注册页
    ├── report.html     # 发布招领页
    ├── item_detail.html # 物品详情页
    ├── claim.html      # 认领物品页
    └── admin.html      # 管理后台页
```

## 数据库表结构

### users 表（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| username | varchar(100) | 用户名 |
| email | varchar(120) | 邮箱 |
| password | varchar(60) | 密码（加密） |
| is_admin | boolean | 是否管理员 |
| phone | varchar(20) | 手机号 |
| created_at | datetime | 创建时间 |

### lost_items 表（失物表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | varchar(100) | 物品名称 |
| description | text | 物品描述 |
| category | varchar(50) | 分类 |
| location | varchar(100) | 发现地点 |
| found_time | datetime | 发现时间 |
| image_filename | varchar(200) | 图片文件名 |
| status | varchar(20) | 状态(pending/claimed/confirmed) |
| reporter_id | int | 发布人ID |
| claimer_name | varchar(100) | 认领人姓名 |
| claimer_phone | varchar(20) | 认领人联系方式 |
| claimed_at | datetime | 认领时间 |
| confirmed_at | datetime | 确认领走时间 |
| created_at | datetime | 创建时间 |

## 清理规则

1. **自动清理**: 物品状态改为「确认领走」后，3天后自动删除数据和图片
2. **手动清理**: 管理员可在后台随时删除任意招领信息

## 注意事项

1. 确保 MySQL 服务正常运行
2. 图片上传目录需有写入权限
3. 生产环境需修改 SECRET_KEY
4. 定时任务需要保持应用运行才能生效

## License

MIT License
