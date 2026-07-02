# api/payment.py
"""
支付核心逻辑 - Lemon Squeezy 集成
"""
import hashlib
import hmac
import json
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from fastapi import HTTPException, status

from api.config import (
    LEMON_SQUEEZY_API_KEY,
    LEMON_SQUEEZY_STORE_ID,
    LEMON_SQUEEZY_WEBHOOK_SECRET,
    PRODUCT_PRO_VARIANT_ID,
    PRODUCT_PRO_MAX_VARIANT_ID,
    PRODUCT_ENTERPRISE_VARIANT_ID,
)
from api.database import db
from api.auth import create_access_token
from utils.logger import log_info, log_error


# ===== 产品映射 =====
PRODUCT_MAP = {
    "pro": {
        "variant_id": PRODUCT_PRO_VARIANT_ID,
        "name": "Regula Pro",
        "price": 299,
        "currency": "CNY"
    },
    "promax": {
        "variant_id": PRODUCT_PRO_MAX_VARIANT_ID,
        "name": "Regula Pro Max",
        "price": 999,
        "currency": "CNY"
    },
    "enterprise": {
        "variant_id": PRODUCT_ENTERPRISE_VARIANT_ID,
        "name": "Regula Enterprise",
        "price": 4999,
        "currency": "CNY"
    }
}


def generate_order_id() -> str:
    """生成订单号"""
    from datetime import datetime
    import secrets
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(4).upper()
    return f"REG-{timestamp}-{random_suffix}"


async def create_checkout(
    product_type: str,
    customer_email: str,
    machine_id: str,
    customer_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建 Lemon Squeezy 结账链接
    """
    product = PRODUCT_MAP.get(product_type)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"未知产品类型: {product_type}"
        )
    
    # 生成订单号
    order_id = generate_order_id()
    
    # 构建 Lemon Squeezy 结账数据
    checkout_data = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "product_options": {
                    "enabled_variants": [product["variant_id"]],
                    "redirect_url": "https://regula.com/payment/success",
                    "receipt_button_text": "返回 Regula",
                    "receipt_thank_you_note": "感谢购买 Regula！激活码将在支付完成后发送到您的邮箱。"
                },
                "checkout_data": {
                    "email": customer_email,
                    "name": customer_name or customer_email,
                    "custom": {
                        "order_id": order_id,
                        "machine_id": machine_id
                    }
                }
            },
            "relationships": {
                "store": {
                    "data": {
                        "type": "stores",
                        "id": LEMON_SQUEEZY_STORE_ID
                    }
                },
                "variant": {
                    "data": {
                        "type": "variants",
                        "id": str(product["variant_id"])
                    }
                }
            }
        }
    }
    
    # 调用 Lemon Squeezy API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.lemonsqueezy.com/v1/checkouts",
            headers={
                "Authorization": f"Bearer {LEMON_SQUEEZY_API_KEY}",
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json"
            },
            json=checkout_data
        )
        
        if response.status_code != 201:
            log_error(f"Lemon Squeezy 创建结账失败: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="支付服务暂时不可用，请稍后重试"
            )
        
        data = response.json()
        checkout_url = data["data"]["attributes"]["url"]
        
        # 保存订单到数据库
        await db.create_order(
            order_id=order_id,
            product_type=product_type,
            customer_email=customer_email,
            machine_id=machine_id,
            amount=product["price"],
            checkout_url=checkout_url,
            customer_name=customer_name
        )
        
        log_info(f"订单创建成功: {order_id} -> {checkout_url}")
        
        return {
            "order_id": order_id,
            "checkout_url": checkout_url
        }


async def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """验证 Webhook 签名"""
    if not LEMON_SQUEEZY_WEBHOOK_SECRET:
        return True  # 如果没有配置密钥，跳过验证
    
    expected = hmac.new(
        LEMON_SQUEEZY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


async def handle_webhook_event(event_name: str, payload: dict):
    """处理 Webhook 事件"""
    log_info(f"收到 Webhook 事件: {event_name}")
    
    if event_name == "order_created":
        # 订单创建事件，暂不处理，等待支付完成
        pass
    
    elif event_name == "order_paid":
        # 支付成功，生成激活码
        await handle_order_paid(payload)


async def handle_order_paid(payload: dict):
    """处理支付成功事件"""
    try:
        order_data = payload.get("data", {})
        attributes = order_data.get("attributes", {})
        custom_data = attributes.get("custom", {})
        
        order_id = custom_data.get("order_id")
        machine_id = custom_data.get("machine_id")
        customer_email = attributes.get("user_email", "")
        lemon_order_id = order_data.get("id")
        
        if not order_id:
            log_error("Webhook: 缺少 order_id")
            return
        
        # 获取产品类型（从价格判断）
        product_type = "pro"  # 默认
        amount = attributes.get("total", 0)
        if amount >= 4000:
            product_type = "enterprise"
        elif amount >= 800:
            product_type = "promax"
        
        # 生成激活码（复用现有授权逻辑）
        from api.auth import hash_password
        from api.database import db
        
        # 获取用户信息（如果已注册则使用现有用户，否则创建）
        user = await db.get_user_by_username(f"user_{customer_email[:16]}")
        if not user:
            # 创建用户
            user_id = await db.create_user(
                username=f"user_{customer_email[:16]}",
                email=customer_email,
                password_hash=hash_password(machine_id[:16] + customer_email[:8])
            )
        else:
            user_id = user['id']
        
        # 生成激活码（根据产品类型不同）
        activation_code = await generate_activation_code(machine_id, product_type)
        
        # 更新订单
        await db.update_order_status(
            order_id=order_id,
            status="paid",
            activation_code=activation_code,
            lemon_order_id=lemon_order_id
        )
        
        # 发送激活码邮件
        await send_activation_email(
            email=customer_email,
            order_id=order_id,
            product_type=product_type,
            activation_code=activation_code,
            machine_id=machine_id
        )
        
        log_info(f"订单支付成功: {order_id}, 激活码: {activation_code[:16]}...")
        
    except Exception as e:
        log_error(f"处理支付成功事件失败: {str(e)}")
        import traceback
        log_error(traceback.format_exc())


async def generate_activation_code(machine_id: str, product_type: str) -> str:
    """生成激活码（复用 license_manager 逻辑）"""
    import base64
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    
    # 根据产品类型选择私钥
    if product_type == "enterprise" or product_type == "promax":
        # Pro Max / Enterprise 使用 Pro Max 私钥（或独立私钥）
        # 这里复用 Pro Max 私钥，你可以为 Enterprise 独立生成
        from config import PRO_MAX_ACTIVATED
        # 简化：使用 Pro 私钥 + 产品类型标识
        private_key_pem = get_private_key(product_type)
    else:
        # Pro 使用 Pro 私钥
        private_key_pem = get_private_key("pro")
    
    if not private_key_pem:
        log_error("私钥未配置，无法生成激活码")
        # fallback: 生成一个临时激活码（仅用于测试）
        import secrets
        return f"TEST-{secrets.token_hex(16)}"
    
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )
    
    # 签名机器码 + 产品类型（保证不同产品激活码不同）
    data = f"{machine_id}:{product_type}"
    signature = private_key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def get_private_key(product_type: str) -> str:
    """获取私钥（从环境变量或文件）"""
    import os
    # 优先从环境变量读取
    key_var = f"PRIVATE_KEY_{product_type.upper()}"
    key = os.getenv(key_var, "")
    if key:
        return key
    
    # 从文件读取
    key_file = f"private_{product_type}.pem"
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read()
    
    return ""


async def send_activation_email(email: str, order_id: str, product_type: str,
                                activation_code: str, machine_id: str):
    """发送激活码邮件"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from api.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
    
    # 产品名称映射
    product_names = {
        "pro": "Regula Pro",
        "promax": "Regula Pro Max",
        "enterprise": "Regula Enterprise"
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Regula 激活码</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a1a2e; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: #fff; margin: 0;">🦅 Regula</h1>
            <p style="color: #8e44ad; margin: 5px 0 0;">合规鹰眼 · 激活码</p>
        </div>
        <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2>感谢您的购买！</h2>
            <p>您已成功购买 <strong>{product_names.get(product_type, product_type)}</strong>。</p>
            <p>您的激活码如下：</p>
            <div style="background: #fff; border: 2px dashed #8e44ad; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                <code style="font-size: 20px; font-weight: bold; color: #1a1a2e;">{activation_code}</code>
            </div>
            <p style="color: #7f8c8d; font-size: 14px;">订单号：<strong>{order_id}</strong></p>
            <p style="color: #7f8c8d; font-size: 14px;">设备指纹：<strong>{machine_id[:32]}...</strong></p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <h3>📌 如何使用</h3>
            <ol>
                <li>打开 Regula 软件</li>
                <li>点击「升级 Pro」或「升级 Pro Max」</li>
                <li>粘贴上面的激活码</li>
                <li>点击「激活」即可解锁全部功能</li>
            </ol>
            <p style="color: #7f8c8d; font-size: 12px; text-align: center; margin-top: 30px;">
                此激活码仅限当前设备使用，请勿分享。<br>
                如有任何问题，请联系 Regula_Official@outlook.com
            </p>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = email
    msg['Subject'] = f"🦅 Regula 激活码 - {product_names.get(product_type, product_type)}"
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        log_info(f"激活邮件已发送: {email}")
    except Exception as e:
        log_error(f"发送邮件失败: {str(e)}")
        # 不抛出异常，避免影响主流程