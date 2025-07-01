#配置文件

import os
from dotenv import load_dotenv

# 加载环境变量文件
load_dotenv()

class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'  # 用于会话安全
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fitness.db'  # 数据库连接
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用SQLAlchemy事件系统
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'  # JWT签名密钥
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 令牌有效期（秒）
