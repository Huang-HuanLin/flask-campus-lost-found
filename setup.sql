-- 创建数据库
CREATE DATABASE IF NOT EXISTS lost_found CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE lost_found;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建失物表
CREATE TABLE IF NOT EXISTS lost_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    found_time DATETIME,
    image_filename VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    reporter_id INT NOT NULL,
    claimer_name VARCHAR(100),
    claimer_phone VARCHAR(20),
    claimed_at DATETIME,
    confirmed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX idx_lost_items_status ON lost_items(status);
CREATE INDEX idx_lost_items_category ON lost_items(category);
CREATE INDEX idx_lost_items_reporter_id ON lost_items(reporter_id);
