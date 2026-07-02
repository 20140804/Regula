# api/exceptions.py
"""
统一异常定义 - 所有API异常集中管理
"""
from typing import Optional, Any, Dict


class APIException(Exception):
    """API 异常基类"""
    def __init__(
        self,
        code: int = 500,
        message: str = "服务器内部错误",
        data: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(self.message)


class BadRequestError(APIException):
    """400 请求错误"""
    def __init__(self, message: str = "请求参数错误", data: Optional[Dict] = None):
        super().__init__(code=400, message=message, data=data)


class UnauthorizedError(APIException):
    """401 未授权"""
    def __init__(self, message: str = "请先登录", data: Optional[Dict] = None):
        super().__init__(code=401, message=message, data=data)


class ForbiddenError(APIException):
    """403 无权限"""
    def __init__(self, message: str = "权限不足", data: Optional[Dict] = None):
        super().__init__(code=403, message=message, data=data)


class NotFoundError(APIException):
    """404 资源不存在"""
    def __init__(self, message: str = "资源不存在", data: Optional[Dict] = None):
        super().__init__(code=404, message=message, data=data)


class RateLimitError(APIException):
    """429 请求过频"""
    def __init__(self, message: str = "请求过于频繁，请稍后重试", data: Optional[Dict] = None):
        super().__init__(code=429, message=message, data=data)


class InternalError(APIException):
    """500 内部错误"""
    def __init__(self, message: str = "服务器内部错误", data: Optional[Dict] = None):
        super().__init__(code=500, message=message, data=data)