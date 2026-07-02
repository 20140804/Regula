# api/webhook_routes.py
"""
Lemon Squeezy Webhook 接收端点
"""
import json
from fastapi import APIRouter, Request, Response, HTTPException, status
from api.payment import verify_webhook_signature, handle_webhook_event
from utils.logger import log_info, log_error

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhook"])


@router.post("/lemon-squeezy")
async def lemon_squeezy_webhook(request: Request):
    """
    Lemon Squeezy Webhook 接收端点
    在 Lemon Squeezy 后台配置此 URL
    """
    try:
        # 获取原始请求体
        payload = await request.body()
        
        # 获取签名
        signature = request.headers.get("x-signature", "")
        
        # 验证签名（可选）
        # if not await verify_webhook_signature(payload, signature):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # 解析 JSON
        data = json.loads(payload)
        
        # 获取事件类型
        event_name = data.get("meta", {}).get("event_name", "")
        
        # 处理事件
        await handle_webhook_event(event_name, data)
        
        return Response(status_code=200)
        
    except json.JSONDecodeError as e:
        log_error(f"Webhook JSON 解析失败: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        log_error(f"Webhook 处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")