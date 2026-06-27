# utils/logger.py
"""
调试日志记录器 - Pro 版专属
记录程序运行中的异常、错误和关键操作
"""
import os
import sys
import traceback
from datetime import datetime
from typing import Optional
from config import PRO_ACTIVATED

DEBUG_LOG_FILE = "debug.txt"


def log_exception(e: Exception, context: str = ""):
    """
    记录异常信息到 debug.txt
    仅在 Pro 激活时生效
    """
    if not PRO_ACTIVATED:
        return
    
    try:
        with open(DEBUG_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n{'='*60}\n")
            f.write(f"[{timestamp}] 异常发生\n")
            if context:
                f.write(f"上下文: {context}\n")
            f.write(f"异常类型: {type(e).__name__}\n")
            f.write(f"异常信息: {str(e)}\n")
            f.write("堆栈跟踪:\n")
            f.write(traceback.format_exc())
            f.write(f"{'='*60}\n")
    except:
        # 日志写入失败不影响主程序
        pass


def log_info(message: str):
    """
    记录信息日志
    仅在 Pro 激活时生效
    """
    if not PRO_ACTIVATED:
        return
    
    try:
        with open(DEBUG_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] INFO: {message}\n")
    except:
        pass


def log_error(message: str):
    """
    记录错误日志（非异常）
    仅在 Pro 激活时生效
    """
    if not PRO_ACTIVATED:
        return
    
    try:
        with open(DEBUG_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ERROR: {message}\n")
    except:
        pass


def clear_debug_log():
    """清空调试日志（可选）"""
    if os.path.exists(DEBUG_LOG_FILE):
        try:
            os.remove(DEBUG_LOG_FILE)
        except:
            pass