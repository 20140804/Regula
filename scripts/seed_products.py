# scripts/seed_products.py
"""
初始化 Lemon Squeezy 产品数据
首次运行前执行，用于同步产品 Variant IDs
"""
import asyncio
import httpx
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import LEMON_SQUEEZY_API_KEY, LEMON_SQUEEZY_STORE_ID
from api.database import db
from utils.logger import setup_logging, log_info, log_error

# 产品定义
PRODUCTS = [
    {
        "id": "pro",
        "name": "Regula Pro",
        "variant_id_key": "PRODUCT_PRO_VARIANT_ID",
        "price": 299,
        "currency": "CNY",
        "description": "OCR图片识别 · 规则模板库 · 高级PDF报告 · 多语言扫描"
    },
    {
        "id": "promax",
        "name": "Regula Pro Max",
        "variant_id_key": "PRODUCT_PRO_MAX_VARIANT_ID",
        "price": 999,
        "currency": "CNY",
        "description": "AI语义理解 · 违规自动分类 · 智能修改建议 · Pro Max专属标识"
    },
    {
        "id": "enterprise",
        "name": "Regula Enterprise",
        "variant_id_key": "PRODUCT_ENTERPRISE_VARIANT_ID",
        "price": 4999,
        "currency": "CNY",
        "description": "API服务 · 在线仪表盘 · Webhook通知 · SSO登录 · 云端规则共享"
    }
]


def generate_env_content(products_data: list) -> str:
    """生成 .env 文件内容"""
    lines = []
    for p in products_data:
        variant_id = p.get('variant_id', 0)
        lines.append(f"{p['variant_id_key']}={variant_id}")
    return "\n".join(lines)


async def fetch_variant_from_lemon(product_name: str) -> int:
    """
    从 Lemon Squeezy 获取产品的 Variant ID
    需要在 Lemon Squeezy 后台已创建产品并配置好
    """
    if not LEMON_SQUEEZY_API_KEY:
        log_error("LEMON_SQUEEZY_API_KEY 未配置")
        return 0
    
    async with httpx.AsyncClient() as client:
        try:
            # 获取所有 Variants
            response = await client.get(
                "https://api.lemonsqueezy.com/v1/variants",
                headers={
                    "Authorization": f"Bearer {LEMON_SQUEEZY_API_KEY}",
                    "Accept": "application/vnd.api+json"
                }
            )
            
            if response.status_code != 200:
                log_error(f"获取 Variants 失败: {response.text}")
                return 0
            
            data = response.json()
            variants = data.get("data", [])
            
            # 查找匹配的产品
            for variant in variants:
                attrs = variant.get("attributes", {})
                name = attrs.get("name", "")
                if product_name in name:
                    log_info(f"找到 Variant: {name} -> ID: {variant['id']}")
                    return int(variant["id"])
            
            log_error(f"未找到产品: {product_name}")
            return 0
            
        except Exception as e:
            log_error(f"获取 Variant 失败: {str(e)}")
            return 0


async def seed_products(update_env: bool = True):
    """初始化产品数据"""
    setup_logging()
    log_info("🔄 开始初始化产品数据...")
    
    # 1. 从 Lemon Squeezy 获取 Variant IDs
    log_info("📡 从 Lemon Squeezy 获取 Variant IDs...")
    products_with_ids = []
    
    for product in PRODUCTS:
        variant_id = await fetch_variant_from_lemon(product["name"])
        product["variant_id"] = variant_id
        products_with_ids.append(product)
        if variant_id:
            log_info(f"✅ {product['name']} -> Variant ID: {variant_id}")
        else:
            log_warning(f"⚠️ 未找到 {product['name']} 的 Variant ID，请手动配置")
    
    # 2. 更新 .env 文件
    if update_env:
        env_content = generate_env_content(products_with_ids)
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        # 读取现有 .env
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                existing = f.read()
        else:
            existing = ""
        
        # 更新或追加
        lines = existing.split('\n')
        new_lines = []
        variant_keys = [p['variant_id_key'] for p in products_with_ids]
        
        for line in lines:
            if any(line.startswith(key) for key in variant_keys):
                continue
            new_lines.append(line)
        
        new_lines.append("\n# ===== 产品 Variant IDs（由 seed_products.py 自动生成）=====")
        for line in env_content.split('\n'):
            if line:
                new_lines.append(line)
        
        # 写入 .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        log_info(f"✅ .env 文件已更新: {env_path}")
    
    # 3. 初始化数据库
    await db.init()
    log_info("✅ 数据库已初始化")
    
    # 4. 输出总结
    print("\n" + "=" * 60)
    print("📊 产品初始化完成")
    print("=" * 60)
    for product in products_with_ids:
        status = f"✅ {product['variant_id']}" if product['variant_id'] else "❌ 未配置"
        print(f"  {product['name']}: {status}")
    print("=" * 60)
    
    if any(p['variant_id'] == 0 for p in products_with_ids):
        print("\n⚠️ 部分产品未找到 Variant ID，请：")
        print("1. 在 Lemon Squeezy 后台创建产品")
        print("2. 手动将 Variant ID 填入 .env 文件")
    else:
        print("\n✅ 所有产品已就绪，可以启动支付服务！")


async def main():
    await seed_products(update_env=True)


if __name__ == "__main__":
    asyncio.run(main())