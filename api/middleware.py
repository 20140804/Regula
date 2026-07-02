# api/middleware.py
"""
中间件：统一日志 + 限流 + 异常捕获
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from limits import RateLimitItemPerMinute
from limits.strategies import MovingWindowRateLimiter
from limits.storage import MemoryStorage

from api.exceptions import RateLimitError, APIException
from api.config import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_ENABLED
from utils.logger import log_info, log_error, log_warning


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # 记录请求
        log_info(f"请求开始: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # 记录响应
            elapsed = (time.time() - start_time) * 1000
            log_info(
                f"请求完成: {request.method} {request.url.path} "
                f"状态码: {response.status_code} 耗时: {elapsed:.2f}ms"
            )
            return response
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            log_error(f"请求异常: {request.method} {request.url.path} {str(e)} 耗时: {elapsed:.2f}ms")
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.storage = MemoryStorage()
        self.strategy = MovingWindowRateLimiter(self.storage)
    
    async def dispatch(self, request: Request, call_next: Callable):
        if not RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # 获取客户端标识（IP + API Key）
        client_id = request.headers.get("X-API-Key") or request.client.host
        
        # 创建限流规则
        rate_limit = RateLimitItemPerMinute(RATE_LIMIT_PER_MINUTE)
        
        # 检查是否超出限制
        if not self.strategy.test(rate_limit, client_id):
            raise RateLimitError(
                message=f"请求过于频繁，请稍后重试（限制: {RATE_LIMIT_PER_MINUTE}次/分钟）"
            )
        
        # 消耗一个额度
        self.strategy.hit(rate_limit, client_id)
        
        return await call_next(request)