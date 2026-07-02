# api/payment_routes.py
"""
支付路由 - 创建订单、查询订单
"""
from fastapi import APIRouter, Depends, HTTPException, status
from api.models import OrderCreate, OrderResponse, CheckoutResponse
from api.payment import create_checkout, PRODUCT_MAP
from api.database import db
from api.auth import get_current_user

router = APIRouter(prefix="/api/v1/payment", tags=["支付"])


@router.get("/products")
async def list_products():
    """列出所有可购买产品"""
    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": "pro",
                "name": "Regula Pro",
                "price": 299,
                "currency": "CNY",
                "description": "OCR图片识别 · 规则模板库 · 高级PDF报告 · 多语言扫描"
            },
            {
                "id": "promax",
                "name": "Regula Pro Max",
                "price": 999,
                "currency": "CNY",
                "description": "AI语义理解 · 违规自动分类 · 智能修改建议 · Pro Max专属标识"
            },
            {
                "id": "enterprise",
                "name": "Regula Enterprise",
                "price": 4999,
                "currency": "CNY",
                "description": "API服务 · 在线仪表盘 · Webhook通知 · SSO登录 · 云端规则共享 · 私有化部署"
            }
        ]
    }


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_endpoint(order: OrderCreate):
    """创建结账链接"""
    # 验证产品类型
    if order.product_type not in PRODUCT_MAP:
        return CheckoutResponse(
            success=False,
            order_id="",
            checkout_url="",
            error=f"未知产品类型: {order.product_type}"
        )
    
    try:
        result = await create_checkout(
            product_type=order.product_type,
            customer_email=order.customer_email,
            machine_id=order.machine_id,
            customer_name=order.customer_name
        )
        return CheckoutResponse(
            success=True,
            order_id=result["order_id"],
            checkout_url=result["checkout_url"]
        )
    except Exception as e:
        return CheckoutResponse(
            success=False,
            order_id="",
            checkout_url="",
            error=str(e)
        )


@router.get("/order/{order_id}")
async def get_order(order_id: str):
    """查询订单状态"""
    order = await db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "order_id": order['order_id'],
            "product_type": order['product_type'],
            "status": order['status'],
            "amount": order['amount'],
            "activation_code": order.get('activation_code'),
            "created_at": order['created_at'],
            "paid_at": order.get('paid_at')
        }
    }


@router.get("/orders/me")
async def my_orders(user: dict = Depends(get_current_user)):
    """获取当前用户的订单列表"""
    orders = await db.get_user_orders(user.get('email'))
    return {
        "code": 200,
        "message": "success",
        "data": orders
    }