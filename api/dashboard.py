# api/dashboard.py
"""
仪表盘后端
"""
from fastapi import APIRouter, Depends
from api.database import db
from api.auth import get_current_user
from api.models import DashboardStats, ScanResponse

router = APIRouter(prefix="/api/v1/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(user: dict = Depends(get_current_user)):
    stats = await db.get_stats(user_id=user['id'])
    recent = await db.get_recent_scans(user_id=user['id'], limit=10)
    
    violations_by_category = {}
    for scan in recent:
        import json
        try:
            for v in json.loads(scan.get('violations_json', '[]')):
                cat = v.get('category', '未分类')
                violations_by_category[cat] = violations_by_category.get(cat, 0) + 1
        except:
            pass
    
    return DashboardStats(
        total_scans=stats.get('total_scans', 0),
        total_violations=stats.get('total_violations', 0),
        fatal_violations=stats.get('fatal_count', 0),
        serious_violations=stats.get('serious_count', 0),
        normal_violations=stats.get('normal_count', 0),
        recent_scans=[ScanResponse(**s) for s in recent],
        violations_by_category=violations_by_category
    )