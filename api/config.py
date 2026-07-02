# api/config.py
"""
API 服务配置 - Enterprise 最终版
支持配置热加载（修改 .env 后自动生效）
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """配置类 - 支持热加载"""
    
    # ===== 基础配置 =====
    @property
    def SECRET_KEY(self) -> str:
        return os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite:///./regula_enterprise.db")
    
    @property
    def DATABASE_PATH(self) -> str:
        """返回纯文件路径（不含 sqlite:///）"""
        url = self.DATABASE_URL
        if url.startswith("sqlite:///"):
            return url[10:]
        return url
    
    @property
    def API_KEYS(self) -> list:
        return os.getenv("API_KEYS", "regula_api_2024_secure_key").split(",")
    
    @property
    def MAX_FILE_SIZE_MB(self) -> int:
        return int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    @property
    def DEBUG(self) -> bool:
        return os.getenv("DEBUG", "true").lower() == "true"
    
    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", "8000"))
    
    # ===== Webhook 配置 =====
    @property
    def WEBHOOK_ENABLED(self) -> bool:
        return os.getenv("WEBHOOK_ENABLED", "true").lower() == "true"
    
    @property
    def WEBHOOK_TIMEOUT(self) -> int:
        return int(os.getenv("WEBHOOK_TIMEOUT", "5"))
    
    @property
    def WEBHOOK_URLS(self) -> list:
        urls = os.getenv("WEBHOOK_URLS", "")
        return urls.split(",") if urls else []
    
    # ===== JWT 配置 =====
    @property
    def JWT_ALGORITHM(self) -> str:
        return os.getenv("JWT_ALGORITHM", "HS256")
    
    @property
    def JWT_EXPIRE_DAYS(self) -> int:
        return int(os.getenv("JWT_EXPIRE_DAYS", "7"))
    
    @property
    def JWT_REFRESH_EXPIRE_DAYS(self) -> int:
        return int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "30"))
    
    # ===== 限流配置 =====
    @property
    def RATE_LIMIT_ENABLED(self) -> bool:
        return os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    @property
    def RATE_LIMIT_PER_MINUTE(self) -> int:
        return int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # ===== 日志配置 =====
    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def LOG_FILE_ENABLED(self) -> bool:
        return os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
    
    @property
    def LOG_FILE_PATH(self) -> str:
        return os.getenv("LOG_FILE_PATH", "logs/regula.log")
    
    @property
    def LOG_MAX_SIZE_MB(self) -> int:
        return int(os.getenv("LOG_MAX_SIZE_MB", "10"))
    
    @property
    def LOG_BACKUP_COUNT(self) -> int:
        return int(os.getenv("LOG_BACKUP_COUNT", "10"))
    
    # ===== 支付配置 =====
    @property
    def LEMON_SQUEEZY_API_KEY(self) -> str:
        return os.getenv("LEMON_SQUEEZY_API_KEY", "")
    
    @property
    def LEMON_SQUEEZY_STORE_ID(self) -> str:
        return os.getenv("LEMON_SQUEEZY_STORE_ID", "")
    
    @property
    def LEMON_SQUEEZY_WEBHOOK_SECRET(self) -> str:
        return os.getenv("LEMON_SQUEEZY_WEBHOOK_SECRET", "")
    
    @property
    def PRODUCT_PRO_VARIANT_ID(self) -> int:
        return int(os.getenv("PRODUCT_PRO_VARIANT_ID", "0"))
    
    @property
    def PRODUCT_PRO_MAX_VARIANT_ID(self) -> int:
        return int(os.getenv("PRODUCT_PRO_MAX_VARIANT_ID", "0"))
    
    @property
    def PRODUCT_ENTERPRISE_VARIANT_ID(self) -> int:
        return int(os.getenv("PRODUCT_ENTERPRISE_VARIANT_ID", "0"))
    
    # ===== 邮件配置 =====
    @property
    def SMTP_HOST(self) -> str:
        return os.getenv("SMTP_HOST", "smtp.gmail.com")
    
    @property
    def SMTP_PORT(self) -> int:
        return int(os.getenv("SMTP_PORT", "587"))
    
    @property
    def SMTP_USER(self) -> str:
        return os.getenv("SMTP_USER", "")
    
    @property
    def SMTP_PASSWORD(self) -> str:
        return os.getenv("SMTP_PASSWORD", "")
    
    @property
    def SMTP_FROM(self) -> str:
        return os.getenv("SMTP_FROM", "Regula <noreply@regula.com>")


# ===== 全局配置实例 =====
config = Config()

# ===== 导出常用配置（兼容旧代码） =====
SECRET_KEY = config.SECRET_KEY
DATABASE_URL = config.DATABASE_URL
DATABASE_PATH = config.DATABASE_PATH
API_KEYS = config.API_KEYS
MAX_FILE_SIZE_MB = config.MAX_FILE_SIZE_MB
DEBUG = config.DEBUG
PORT = config.PORT
WEBHOOK_ENABLED = config.WEBHOOK_ENABLED
WEBHOOK_TIMEOUT = config.WEBHOOK_TIMEOUT
WEBHOOK_URLS = config.WEBHOOK_URLS
RATE_LIMIT_ENABLED = config.RATE_LIMIT_ENABLED
RATE_LIMIT_PER_MINUTE = config.RATE_LIMIT_PER_MINUTE
LOG_FILE_PATH = config.LOG_FILE_PATH
LOG_LEVEL = config.LOG_LEVEL

# ===== 支付配置导出 =====
LEMON_SQUEEZY_API_KEY = config.LEMON_SQUEEZY_API_KEY
LEMON_SQUEEZY_STORE_ID = config.LEMON_SQUEEZY_STORE_ID
LEMON_SQUEEZY_WEBHOOK_SECRET = config.LEMON_SQUEEZY_WEBHOOK_SECRET
PRODUCT_PRO_VARIANT_ID = config.PRODUCT_PRO_VARIANT_ID
PRODUCT_PRO_MAX_VARIANT_ID = config.PRODUCT_PRO_MAX_VARIANT_ID
PRODUCT_ENTERPRISE_VARIANT_ID = config.PRODUCT_ENTERPRISE_VARIANT_ID
SMTP_HOST = config.SMTP_HOST
SMTP_PORT = config.SMTP_PORT
SMTP_USER = config.SMTP_USER
SMTP_PASSWORD = config.SMTP_PASSWORD
SMTP_FROM = config.SMTP_FROM