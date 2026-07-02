# api/routes.py
"""
扫描路由 + Webhook 触发
"""
import os
import tempfile
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from api.models import (
    ScanRequest, BatchScanRequest, ScanResponse, BatchScanResponse,
    ViolationResponse, HealthResponse
)
from api.dependencies import verify_api_key
from api.webhook import webhook_manager
from api.database import db
from core.rule_engine import RuleEngine
from core.doc_parser import DocParser
from core.ai_engine import is_ai_available
from core.ai_suggester import AISuggester
from config import PRO_ACTIVATED, PRO_MAX_ACTIVATED, FEATURES
from utils.logger import log_info

router = APIRouter()


async def perform_scan(text: str, filename: str = None, user_id: int = None) -> ScanResponse:
    try:
        engine = RuleEngine()
        violations = engine.scan(text)
        
        if PRO_ACTIVATED and PRO_MAX_ACTIVATED and is_ai_available():
            violations = AISuggester.enhance_batch(violations)
        
        fatal = sum(1 for v in violations if v.severity == "致命")
        serious = sum(1 for v in violations if v.severity == "严重")
        normal = sum(1 for v in violations if v.severity == "一般")
        
        response = ScanResponse(
            success=True,
            filename=filename,
            total_violations=len(violations),
            fatal_count=fatal,
            serious_count=serious,
            normal_count=normal,
            violations=[
                ViolationResponse(
                    keyword=v.keyword,
                    context=v.context[:200],
                    line_num=v.line_num,
                    severity=v.severity,
                    position=v.position,
                    suggestion=v.suggestion,
                    category=getattr(v, 'category', None),
                    confidence=getattr(v, 'confidence', None),
                )
                for v in violations
            ],
            scanned_at=datetime.now()
        )
        
        # 保存到数据库
        if user_id:
            await db.save_scan(user_id, filename, text, violations, {
                'total': len(violations), 'fatal': fatal, 'serious': serious, 'normal': normal
            })
        
        # 触发 Webhook
        await webhook_manager.notify({
            "event": "scan.completed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "filename": filename,
                "total_violations": len(violations),
                "fatal_count": fatal,
                "serious_count": serious,
                "normal_count": normal,
                "violations": [
                    {"keyword": v.keyword, "severity": v.severity, "suggestion": v.suggestion}
                    for v in violations
                ]
            }
        })
        
        return response
    except Exception as e:
        return ScanResponse(success=False, error=str(e), scanned_at=datetime.now())


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy", version="1.2.0",
        features={"pro": PRO_ACTIVATED, "pro_max": PRO_MAX_ACTIVATED,
                  "ai": is_ai_available(), "ocr": FEATURES.get("ocr", False)}
    )


@router.post("/scan", response_model=ScanResponse)
async def scan_text(request: ScanRequest, api_key: str = Depends(verify_api_key)):
    return await perform_scan(request.text, request.filename)


@router.post("/scan/batch", response_model=BatchScanResponse)
async def scan_batch(request: BatchScanRequest, api_key: str = Depends(verify_api_key)):
    results = []
    total = 0
    for idx, text in enumerate(request.texts):
        filename = request.filenames[idx] if request.filenames and idx < len(request.filenames) else f"文档_{idx+1}"
        result = await perform_scan(text, filename)
        results.append(result)
        if result.success:
            total += result.total_violations
    return BatchScanResponse(success=True, total_files=len(request.texts), total_violations=total, results=results)


@router.post("/scan/upload", response_model=ScanResponse)
async def scan_upload(file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="仅支持 .docx 格式")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        parser = DocParser()
        full_text, _ = parser.parse_docx(tmp_path)
        return await perform_scan(full_text, file.filename)
    finally:
        os.unlink(tmp_path)