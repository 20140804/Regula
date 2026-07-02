# api/models.py
"""
API 数据模型 - Enterprise 最终版
包含：认证、扫描、批量、文件、仪表盘、统一响应
"""
from typing import List, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field


# ===== 统一响应模型 =====
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


# ===== 认证模型 =====
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str = "user"
    created_at: datetime
    last_login: Optional[datetime] = None


class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    user: Optional[UserResponse] = None
    error: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


# ===== 扫描请求模型 =====
class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="要扫描的文本内容")
    filename: Optional[str] = Field(None, description="文件名（可选）")


class BatchScanRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, description="多个文本内容列表")
    filenames: Optional[List[str]] = Field(None, description="对应的文件名列表（可选）")


class FileScanRequest(BaseModel):
    file_path: str = Field(..., min_length=1, description="服务器端 .docx 文件路径")


# ===== 扫描响应模型 =====
class ViolationResponse(BaseModel):
    keyword: str
    context: str
    line_num: int
    severity: str
    position: str
    suggestion: str
    category: Optional[str] = None
    confidence: Optional[float] = None


class ScanResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    total_violations: int = 0
    fatal_count: int = 0
    serious_count: int = 0
    normal_count: int = 0
    violations: List[ViolationResponse] = []
    scanned_at: Optional[datetime] = None
    error: Optional[str] = None


class BatchScanResponse(BaseModel):
    success: bool
    total_files: int = 0
    total_violations: int = 0
    results: List[ScanResponse] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    features: dict


# ===== 仪表盘模型 =====
class DashboardStats(BaseModel):
    total_scans: int
    total_violations: int
    fatal_violations: int
    serious_violations: int
    normal_violations: int
    recent_scans: List[ScanResponse]
    violations_by_category: dict
    # api/models.py (追加)

# ===== 订单模型 =====
class OrderStatus:
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    """创建订单请求"""
    product_type: str = Field(..., description="pro / promax / enterprise")
    customer_email: str = Field(..., description="用户邮箱")
    customer_name: Optional[str] = None
    machine_id: str = Field(..., description="机器码")


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_id: str
    product_type: str
    customer_email: str
    customer_name: Optional[str]
    amount: float
    currency: str = "CNY"
    status: str
    checkout_url: Optional[str] = None
    activation_code: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None


class CheckoutResponse(BaseModel):
    """结账响应"""
    success: bool
    order_id: str
    checkout_url: str
    error: Optional[str] = None