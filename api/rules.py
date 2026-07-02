# api/rules.py
"""
云端规则共享 - 团队规则库
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from api.database import db
from api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/rules", tags=["规则共享"])


class RuleModel(BaseModel):
    name: str
    keyword: str
    near_keyword: Optional[str] = ""
    max_distance: int = 10
    severity: str = "一般"
    position: str = "任意"
    suggestion: str = ""
    shared: bool = False  # 是否共享给团队


@router.get("/")
async def get_rules(user: dict = Depends(get_current_user)):
    """获取用户的规则（个人 + 团队共享）"""
    async with db.get_connection() as conn:
        # 个人规则
        personal = await conn.execute(
            "SELECT * FROM rules WHERE user_id = ? AND shared = 0",
            (user['id'],)
        )
        personal_rules = await personal.fetchall()
        
        # 团队共享规则
        shared = await conn.execute(
            "SELECT * FROM rules WHERE team_id IS NOT NULL AND shared = 1"
        )
        shared_rules = await shared.fetchall()
        
        return {
            "personal": [dict(r) for r in personal_rules],
            "shared": [dict(r) for r in shared_rules]
        }


@router.post("/")
async def create_rule(rule: RuleModel, user: dict = Depends(get_current_user)):
    """创建规则（可选择共享）"""
    async with db.get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO rules (user_id, name, keyword, near_keyword, max_distance,
                               severity, position, suggestion, shared)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user['id'], rule.name, rule.keyword, rule.near_keyword,
              rule.max_distance, rule.severity, rule.position,
              rule.suggestion, 1 if rule.shared else 0))
        await conn.commit()
        return {"id": cursor.lastrowid, "success": True}


@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, user: dict = Depends(get_current_user)):
    """删除规则（只能删除自己的）"""
    async with db.get_connection() as conn:
        # 验证所有权
        rule = await conn.execute(
            "SELECT user_id FROM rules WHERE id = ?",
            (rule_id,)
        )
        r = await rule.fetchone()
        if not r or r['user_id'] != user['id']:
            raise HTTPException(status_code=403, detail="无权删除此规则")
        
        await conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        await conn.commit()
        return {"success": True}