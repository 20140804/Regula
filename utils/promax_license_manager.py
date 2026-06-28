# utils/promax_license_manager.py
"""
Pro Max 授权管理器 - 独立于 Pro 授权体系
使用独立的 RSA 密钥对
"""
import os
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

PROMAX_LICENSE_FILE = "pro_max.key"

# Pro Max 公钥（与 Pro 授权使用不同的密钥对）
PROMAX_PUBLIC_KEY_PEM = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw8iNkXjX5dLJZ6Qk8x9a
...（你需要生成一对新的 Pro Max 专用密钥对，把公钥放这里）...
-----END PUBLIC KEY-----
"""


def get_machine_id() -> str:
    """复用 Pro 的机器码生成逻辑"""
    from utils.license_manager import get_machine_id as get_id
    return get_id()


def verify_promax_activation(machine_id: str, activation_code: str) -> bool:
    """验证 Pro Max 激活码"""
    if not activation_code or not machine_id:
        return False
    
    try:
        signature = base64.b64decode(activation_code.encode())
        public_key = serialization.load_pem_public_key(
            PROMAX_PUBLIC_KEY_PEM.encode(),
            backend=default_backend()
        )
        public_key.verify(
            signature,
            machine_id.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def is_promax_activated() -> bool:
    """检查 Pro Max 是否已激活"""
    if not os.path.exists(PROMAX_LICENSE_FILE):
        return False
    
    try:
        with open(PROMAX_LICENSE_FILE, 'r') as f:
            activation_code = f.read().strip()
        machine_id = get_machine_id()
        return verify_promax_activation(machine_id, activation_code)
    except Exception:
        return False


def save_promax_activation(activation_code: str) -> bool:
    """保存 Pro Max 激活码到本地文件"""
    try:
        with open(PROMAX_LICENSE_FILE, 'w') as f:
            f.write(activation_code.strip())
        return True
    except Exception:
        return False