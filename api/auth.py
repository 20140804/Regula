# api/auth.py
"""
SSO 认证 - JWT + Google/GitHub + 刷新Token
"""
import jwt
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Header, Request
from api.config import config
from api.database import db
from api.exceptions import UnauthorizedError, ForbiddenError


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return salt + ":" + hashlib.sha256((salt + password).encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    salt, hash_val = hashed.split(":")
    return hashlib.sha256((salt + password).encode()).hexdigest() == hash_val


def create_access_token(user_id: int, username: str, role: str) -> str:
    """创建访问Token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(days=config.JWT_EXPIRE_DAYS)
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """创建刷新Token"""
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(days=config.JWT_REFRESH_EXPIRE_DAYS)
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise UnauthorizedError("无效的Token类型")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token已过期，请刷新")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("无效的Token")


def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise UnauthorizedError("无效的刷新Token")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("刷新Token已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("无效的刷新Token")


async def get_current_user(authorization: str = Header(...)) -> dict:
    """获取当前用户（依赖注入）"""
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("无效的认证头")
    token = authorization[7:]
    payload = verify_access_token(token)
    user = await db.get_user_by_id(payload.get("user_id"))
    if not user:
        raise UnauthorizedError("用户不存在")
    return dict(user)


async def refresh_access_token(refresh_token: str) -> dict:
    """刷新访问Token"""
    payload = verify_refresh_token(refresh_token)
    user = await db.get_user_by_id(payload.get("user_id"))
    if not user:
        raise UnauthorizedError("用户不存在")
    
    new_access_token = create_access_token(user['id'], user['username'], user['role'])
    new_refresh_token = create_refresh_token(user['id'])
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "expires_in": config.JWT_EXPIRE_DAYS * 24 * 3600
    }


# ===== 权限校验工具 =====

def require_role(required_role: str):
    """权限校验装饰器（用于路由）"""
    async def dependency(user: dict = Depends(get_current_user)):
        role_priority = {"admin": 3, "editor": 2, "viewer": 1}
        user_priority = role_priority.get(user.get("role", "viewer"), 0)
        required_priority = role_priority.get(required_role, 0)
        
        if user_priority < required_priority:
            raise ForbiddenError(f"需要 {required_role} 权限，当前为 {user.get('role', 'viewer')}")
        return user
    return dependency


# 预定义的权限依赖
require_admin = require_role("admin")
require_editor = require_role("editor")