# api/webhook.py
"""
Webhook 管理器
"""
import asyncio
from typing import Dict, Any, List
import httpx
from utils.logger import log_info, log_error


class WebhookManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = set()
        return cls._instance
    
    def add_subscriber(self, url: str):
        self._subscribers.add(url)
        log_info(f"Webhook 订阅添加: {url}")
    
    def remove_subscriber(self, url: str):
        self._subscribers.discard(url)
        log_info(f"Webhook 订阅移除: {url}")
    
    def get_subscribers(self) -> List[str]:
        return list(self._subscribers)
    
    async def notify(self, data: Dict[str, Any]):
        if not self._subscribers:
            return
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = [self._send_one(client, url, data) for url in self._subscribers]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_one(self, client: httpx.AsyncClient, url: str, data: Dict[str, Any]):
        try:
            response = await client.post(url, json=data, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            log_info(f"Webhook 发送成功: {url}")
        except Exception as e:
            log_error(f"Webhook 发送失败 ({url}): {e}")
            raise


webhook_manager = WebhookManager()