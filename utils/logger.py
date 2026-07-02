# utils/logger.py
"""
统一日志管理 - 支持按日切割、多级别、结构化输出
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional

from api.config import config


# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 结构化日志格式（JSON）
JSON_LOG_FORMAT = {
    "time": "%(asctime)s",
    "level": "%(levelname)s",
    "module": "%(name)s",
    "message": "%(message)s"
}


def setup_logging():
    """初始化日志系统"""
    # 确保日志目录存在
    log_dir = os.path.dirname(config.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 获取根日志器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    
    # 移除已有的处理器（避免重复）
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件输出（按日切割）
    if config.LOG_FILE_ENABLED:
        file_handler = TimedRotatingFileHandler(
            config.LOG_FILE_PATH,
            when="midnight",
            interval=1,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)


def get_logger(name: str = "regula"):
    """获取日志器"""
    return logging.getLogger(name)


def log_info(message: str, **kwargs):
    """记录 INFO 日志"""
    get_logger().info(message, extra=kwargs)


def log_warning(message: str, **kwargs):
    """记录 WARNING 日志"""
    get_logger().warning(message, extra=kwargs)


def log_error(message: str, **kwargs):
    """记录 ERROR 日志"""
    get_logger().error(message, extra=kwargs)


def log_debug(message: str, **kwargs):
    """记录 DEBUG 日志"""
    get_logger().debug(message, extra=kwargs)


# 初始化日志
try:
    setup_logging()
except Exception:
    # 如果日志初始化失败，确保不会崩溃
    print("⚠️ 日志初始化失败，使用控制台日志")