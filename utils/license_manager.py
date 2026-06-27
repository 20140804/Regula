# utils/license_manager.py
"""
Pro 授权管理 - 基于机器码 + RSA 签名验证
"""
import os
import json
import hashlib
import platform
import uuid
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

LICENSE_FILE = "license.key"
PUBLIC_KEY_PEM = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwlv/Y8IO7qPg+fgfVlt+
hd28xnQU38zgfknGHAHqYhxUOh4amTWDJ6f4qSBPmnqxbVo0y51s4XyuIoz4AolG
RPt7b6bZ9KfcKFLMQsMbS823KW5FsGswTLkzFnAmiMIpW1Y+1T8xrrTg6hlgh5GF
+JR+6Y+2fDvkPCZlhZ4QWMf9All6sy4qGfT1U63WfCMXUTrjK0xe9uFjq7GDIR3O
HoXpnbMrcSgzalJr3fVhtg/ipI1b8Ogo0bnl3cM8Wgyyc/Gp0Eh/MkMsA1WsCymg
TwunDZpFxUaQuAV1YrN3rg8SYWPEfkayne8DXvlC1sk3qhAUMpdI2iGmMMQeLs64
BwIDAQAB
-----END PUBLIC KEY-----
"""


def get_machine_id() -> str:
    """生成唯一的机器码（硬件指纹）"""
    # 组合多个系统信息
    info = [
        platform.node(),           # 主机名
        platform.processor(),      # 处理器
        str(uuid.getnode()),       # MAC 地址
        platform.system(),         # 操作系统
        platform.version()         # 系统版本
    ]
    combined = "|".join(info)
    # 使用 SHA-256 生成固定长度的机器码
    return hashlib.sha256(combined.encode()).hexdigest()


def generate_activation_code(machine_id: str, private_key_pem: str) -> str:
    """
    根据机器码生成激活码（由开发者本地运行，生成后发给用户）
    需要私钥，此函数仅用于开发阶段生成激活码，不会包含在发布的软件中
    """
    # 加载私钥
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )
    # 签名机器码
    signature = private_key.sign(
        machine_id.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    # 返回 base64 编码的签名
    import base64
    return base64.b64encode(signature).decode()


def verify_activation(machine_id: str, activation_code: str) -> bool:
    """
    验证激活码是否有效
    使用内置公钥验证签名
    """
    if not activation_code or not machine_id:
        return False
    
    try:
        import base64
        signature = base64.b64decode(activation_code.encode())
        # 加载公钥
        public_key = serialization.load_pem_public_key(
            PUBLIC_KEY_PEM.encode(),
            backend=default_backend()
        )
        # 验证签名
        public_key.verify(
            signature,
            machine_id.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def is_pro_activated() -> bool:
    """检查当前机器是否已激活 Pro"""
    if not os.path.exists(LICENSE_FILE):
        return False
    
    try:
        with open(LICENSE_FILE, 'r') as f:
            activation_code = f.read().strip()
        machine_id = get_machine_id()
        return verify_activation(machine_id, activation_code)
    except Exception:
        return False


def save_activation(activation_code: str) -> bool:
    """保存激活码到本地文件"""
    try:
        with open(LICENSE_FILE, 'w') as f:
            f.write(activation_code.strip())
        return True
    except Exception:
        return False


def get_pro_status() -> dict:
    """获取 Pro 状态信息"""
    activated = is_pro_activated()
    return {
        "activated": activated,
        "machine_id": get_machine_id() if not activated else None
    }