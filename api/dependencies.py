# api/dependencies.py
"""
API 依赖注入
"""
from fastapi import Header, HTTPException, status, UploadFile, Depends
from api.config import API_KEYS, MAX_FILE_SIZE_MB
from api.auth import require_role


async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    """验证 API Key"""
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key


async def validate_file_size(file: UploadFile):
    """验证文件大小"""
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过 {MAX_FILE_SIZE_MB}MB 限制"
        )
    await file.seek(0)
    return file


# ===== 权限依赖（快捷使用） =====
require_admin = require_role("admin")
require_editor = require_role("editor")
require_viewer = require_role("viewer")