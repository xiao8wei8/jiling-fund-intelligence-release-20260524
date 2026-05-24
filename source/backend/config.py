"""系统配置文件"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../data/fund_marketing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hftf_fund_marketing_2024_secret_key')
    
    # API配置 - MiniMax Anthropic兼容接口
    ANTHROPIC_BASE_URL = os.environ.get('ANTHROPIC_BASE_URL', 'https://api.minimaxi.com/anthropic')
    ANTHROPIC_AUTH_TOKEN = os.environ.get('ANTHROPIC_AUTH_TOKEN', 'sk-cp-YGy8SkUNXx_eeiTBAYtJ_4lMk5dL0yxeGVD9BmLL7kAf_tn7gINVkFlJAkGG9Vp9aoGLMxBlA2E6w0cnO6rAoKlYHdtQfA0bYdsNTRSVEM1ttX_vN2NkHjc')
    ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'MiniMax-M2.7')
    API_TIMEOUT_MS = int(os.environ.get('API_TIMEOUT_MS', '30000'))
    
    # 缓存配置
    CACHE_DURATION = 3600  # 缓存时间（秒）
    
    # 服务配置
    PORT = int(os.environ.get('PORT', 5002))
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
