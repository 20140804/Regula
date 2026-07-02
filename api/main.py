# api/main.py
"""
Regula Enterprise API - 最终完整版
整合：统一错误处理 + 日志聚合 + 刷新Token + 权限细化 + 限流 + 支付系统 + Webhook
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from api.config import config
from api.database import db
from api.auth import (
    get_current_user, create_access_token, create_refresh_token,
    verify_password, hash_password, refresh_access_token
)
from api.routes import router as scan_router
from api.dashboard import router as dashboard_router
from api.webhook import webhook_manager
from api.models import UserLogin, RefreshTokenRequest
from api.rules import router as rules_router
from api.payment_routes import router as payment_router
from api.webhook_routes import router as webhook_router
from api.middleware import LoggingMiddleware, RateLimitMiddleware
from api.exceptions import APIException, UnauthorizedError
from utils.logger import log_info, log_error, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 确保日志目录存在
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    
    # 初始化日志
    setup_logging()
    log_info("🔄 启动 Regula Enterprise API...")
    
    # 初始化数据库
    log_info("🔄 初始化数据库...")
    await db.init()
    log_info("✅ 数据库初始化完成")
    
    # 注册默认 Webhook
    for url in config.WEBHOOK_URLS:
        if url:
            webhook_manager.add_subscriber(url)
            log_info(f"📡 已注册 Webhook: {url}")
    
    # 创建默认管理员
    admin = await db.get_user_by_username("admin")
    if not admin:
        await db.create_user("admin", "admin@regula.local", hash_password("admin123"))
        log_info("👤 默认管理员已创建: admin / admin123")
    
    log_info("🚀 服务启动完成")
    yield
    log_info("🛑 服务关闭")


app = FastAPI(
    title="Regula Enterprise API",
    description="合规鹰眼 - 企业版完整服务",
    version="1.3.0",
    lifespan=lifespan,
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 日志中间件 =====
app.add_middleware(LoggingMiddleware)

# ===== 限流中间件 =====
app.add_middleware(RateLimitMiddleware)


# ===== 统一异常处理器 =====
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.data
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(f"未处理的异常: {str(exc)}")
    import traceback
    log_error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": {"detail": str(exc) if config.DEBUG else None}
        }
    )


# ============================================================
# 认证路由
# ============================================================
from fastapi import APIRouter, Depends
auth_router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@auth_router.post("/login")
async def login(login: UserLogin):
    """用户名密码登录"""
    user = await db.get_user_by_username(login.username)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "用户不存在", "data": None}
        )
    
    if not verify_password(login.password, user['password_hash']):
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "密码错误", "data": None}
        )
    
    await db.update_last_login(user['id'])
    access_token = create_access_token(user['id'], user['username'], user['role'])
    refresh_token = create_refresh_token(user['id'])
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": config.JWT_EXPIRE_DAYS * 24 * 3600,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            }
        }
    }


@auth_router.post("/refresh")
async def refresh(request: RefreshTokenRequest):
    """刷新Token"""
    try:
        result = await refresh_access_token(request.refresh_token)
        return {
            "code": 200,
            "message": "Token刷新成功",
            "data": result
        }
    except UnauthorizedError as e:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": str(e), "data": None}
        )


@auth_router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "created_at": user['created_at'],
            "last_login": user['last_login']
        }
    }


@auth_router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """退出登录（客户端需清除Token）"""
    return {"code": 200, "message": "退出成功", "data": None}


@auth_router.post("/sso/google")
async def google_sso(token: str):
    """Google SSO 登录（简化版）"""
    user = await db.get_user_by_username(f"google_{token[:16]}")
    if not user:
        user_id = await db.create_user(
            f"google_{token[:16]}",
            f"google_{token[:16]}@google.com",
            hash_password(token)
        )
        user = await db.get_user_by_id(user_id)
    
    jwt_token = create_access_token(user['id'], user['username'], user['role'])
    return {"success": True, "access_token": jwt_token}


@auth_router.post("/sso/github")
async def github_sso(token: str):
    """GitHub SSO 登录（简化版）"""
    user = await db.get_user_by_username(f"github_{token[:16]}")
    if not user:
        user_id = await db.create_user(
            f"github_{token[:16]}",
            f"github_{token[:16]}@github.com",
            hash_password(token)
        )
        user = await db.get_user_by_id(user_id)
    
    jwt_token = create_access_token(user['id'], user['username'], user['role'])
    return {"success": True, "access_token": jwt_token}


# ============================================================
# 注册所有路由
# ============================================================
app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(dashboard_router)
app.include_router(rules_router)
app.include_router(payment_router)
app.include_router(webhook_router)


# ============================================================
# 静态文件（前端仪表盘）
# ============================================================
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ============================================================
# 根路径
# ============================================================
@app.get("/")
async def root():
    return {
        "service": "Regula Enterprise API",
        "version": "1.3.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/v1/auth",
            "scan": "/api/v1/scan",
            "dashboard": "/api/v1/dashboard",
            "rules": "/api/v1/rules",
            "payment": "/api/v1/payment",
            "webhooks": "/api/v1/webhooks",
            "docs": "/docs"
        }
    }


# ============================================================
# 启动入口
# ============================================================
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG
    )