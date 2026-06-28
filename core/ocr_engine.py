# core/ocr_engine.py
"""
OCR 图片文字识别引擎 - 基于 PyTesseract（Tesseract OCR 封装）
Pro 版专属功能
"""
import os
import pytesseract
from PIL import Image
from typing import List, Tuple
from config import PRO_ACTIVATED


class OCREngine:
    """OCR 识别引擎（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 检查 Pro 授权，未授权时静默失败（不抛出异常）
        if not PRO_ACTIVATED:
            print("[OCR] Pro 未激活，OCR 功能不可用")
            self._reader = None
            return
        
        # 自动定位 Tesseract 可执行文件
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        tesseract_found = False
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                tesseract_found = True
                print(f"[OCR] Tesseract 已定位: {path}")
                break
        
        if not tesseract_found:
            # 尝试从 PATH 中查找
            import shutil
            tess_path = shutil.which("tesseract")
            if tess_path:
                pytesseract.pytesseract.tesseract_cmd = tess_path
                print(f"[OCR] Tesseract 已从 PATH 定位: {tess_path}")
            else:
                print("[OCR] 警告: 未找到 Tesseract，请确保已正确安装。")
                self._reader = None
                return
        
        self._reader = True  # 标记为可用
    
    def is_available(self) -> bool:
        """检查 OCR 引擎是否可用"""
        if not PRO_ACTIVATED:
            return False
        if self._reader is None:
            return False
        try:
            import subprocess
            result = subprocess.run(
                [pytesseract.pytesseract.tesseract_cmd, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def extract_text(self, image_path: str) -> Tuple[str, List[Tuple[str, float, Tuple]]]:
        """
        从图片中提取文字
        返回: (全文, [(文字, 置信度, 坐标), ...])
        注意：Tesseract 不直接返回置信度和坐标，这里置信度固定为 0.9，坐标为 None
        """
        if not PRO_ACTIVATED:
            raise RuntimeError("OCR 功能需要 Pro 授权，请激活 Pro 版。")
        
        if not self.is_available():
            raise RuntimeError("Tesseract 引擎不可用，请检查安装。")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 使用 PIL 打开图片
        image = Image.open(image_path)
        
        # 执行 OCR（中文 + 英文）
        text = pytesseract.image_to_string(
            image,
            lang='chi_sim+eng',   # 中文简体 + 英文
            config='--oem 3 --psm 6'
        )
        
        # 按行切分，模拟返回格式（与之前接口兼容）
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        # 构造返回格式
        result = []
        for line in lines:
            result.append((line, 0.9, None))  # 置信度占位，坐标无
        
        return "\n".join(lines), result
    
    def extract_text_simple(self, image_path: str) -> str:
        full_text, _ = self.extract_text(image_path)
        return full_text
    
    def get_supported_formats(self) -> List[str]:
        return ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']


# 全局单例
try:
    ocr_engine = OCREngine()
except Exception as e:
    print(f"[OCR] 初始化异常: {e}")
    ocr_engine = None


def is_ocr_available() -> bool:
    return ocr_engine is not None and ocr_engine.is_available()