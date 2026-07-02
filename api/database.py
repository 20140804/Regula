# api/database.py
"""
数据库管理 - Enterprise 最终版
包含：用户、扫描历史、规则共享、订单
"""
import os
import aiosqlite
import json
from typing import Optional, List, Dict
from contextlib import asynccontextmanager
from api.config import DATABASE_PATH


class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_path = DATABASE_PATH
        return cls._instance
    
    async def init(self):
        """初始化数据库表"""
        # 确保目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # ===== 用户表 =====
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # ===== 扫描历史表 =====
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    filename TEXT,
                    text_preview TEXT,
                    total_violations INTEGER DEFAULT 0,
                    fatal_count INTEGER DEFAULT 0,
                    serious_count INTEGER DEFAULT 0,
                    normal_count INTEGER DEFAULT 0,
                    violations_json TEXT,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # ===== 规则共享表 =====
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    team_id INTEGER,
                    name TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    near_keyword TEXT,
                    max_distance INTEGER DEFAULT 10,
                    severity TEXT DEFAULT '一般',
                    position TEXT DEFAULT '任意',
                    suggestion TEXT,
                    shared INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # ===== 订单表 =====
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    product_type TEXT NOT NULL,
                    customer_email TEXT NOT NULL,
                    customer_name TEXT,
                    machine_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'CNY',
                    status TEXT DEFAULT 'pending',
                    checkout_url TEXT,
                    activation_code TEXT,
                    lemon_squeezy_order_id TEXT,
                    paid_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    @asynccontextmanager
    async def get_connection(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db
    
    # ============================================================
    # 用户操作
    # ============================================================
    async def create_user(self, username: str, email: str, password_hash: str) -> int:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_user_by_username(self, username: str):
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            return await cursor.fetchone()
    
    async def get_user_by_email(self, email: str):
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            return await cursor.fetchone()
    
    async def get_user_by_id(self, user_id: int):
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            return await cursor.fetchone()
    
    async def update_last_login(self, user_id: int):
        async with self.get_connection() as db:
            await db.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            await db.commit()
    
    async def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT id, username, email, role, created_at, last_login FROM users LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ============================================================
    # 扫描历史操作
    # ============================================================
    async def save_scan(self, user_id: Optional[int], filename: str, text: str,
                        violations: List, counts: dict) -> int:
        async with self.get_connection() as db:
            cursor = await db.execute("""
                INSERT INTO scan_history (
                    user_id, filename, text_preview,
                    total_violations, fatal_count, serious_count, normal_count,
                    violations_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, filename, text[:500],
                counts.get('total', 0),
                counts.get('fatal', 0),
                counts.get('serious', 0),
                counts.get('normal', 0),
                json.dumps([{
                    'keyword': v.keyword,
                    'severity': v.severity,
                    'line_num': v.line_num,
                    'suggestion': v.suggestion,
                    'category': getattr(v, 'category', None),
                } for v in violations], ensure_ascii=False)
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_recent_scans(self, user_id: Optional[int] = None, limit: int = 20) -> List[Dict]:
        async with self.get_connection() as db:
            if user_id:
                cursor = await db.execute(
                    "SELECT * FROM scan_history WHERE user_id = ? ORDER BY scanned_at DESC LIMIT ?",
                    (user_id, limit)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM scan_history ORDER BY scanned_at DESC LIMIT ?",
                    (limit,)
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        async with self.get_connection() as db:
            if user_id:
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total_scans,
                        SUM(total_violations) as total_violations,
                        SUM(fatal_count) as fatal_count,
                        SUM(serious_count) as serious_count,
                        SUM(normal_count) as normal_count
                    FROM scan_history WHERE user_id = ?
                """, (user_id,))
            else:
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total_scans,
                        SUM(total_violations) as total_violations,
                        SUM(fatal_count) as fatal_count,
                        SUM(serious_count) as serious_count,
                        SUM(normal_count) as normal_count
                    FROM scan_history
                """)
            row = await cursor.fetchone()
            return dict(row) if row else {
                'total_scans': 0, 'total_violations': 0,
                'fatal_count': 0, 'serious_count': 0, 'normal_count': 0
            }
    
    # ============================================================
    # 规则操作
    # ============================================================
    async def save_rule(self, user_id: int, name: str, keyword: str,
                        near_keyword: str, max_distance: int,
                        severity: str, position: str, suggestion: str,
                        shared: bool = False) -> int:
        async with self.get_connection() as db:
            cursor = await db.execute("""
                INSERT INTO rules (
                    user_id, name, keyword, near_keyword, max_distance,
                    severity, position, suggestion, shared
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, name, keyword, near_keyword, max_distance,
                severity, position, suggestion, 1 if shared else 0
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_user_rules(self, user_id: int) -> Dict:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM rules WHERE user_id = ? AND shared = 0",
                (user_id,)
            )
            personal = await cursor.fetchall()
            
            cursor = await db.execute(
                "SELECT * FROM rules WHERE shared = 1"
            )
            shared = await cursor.fetchall()
            
            return {
                "personal": [dict(r) for r in personal],
                "shared": [dict(r) for r in shared]
            }
    
    async def delete_rule(self, rule_id: int, user_id: int) -> bool:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT user_id FROM rules WHERE id = ?",
                (rule_id,)
            )
            row = await cursor.fetchone()
            if not row or row['user_id'] != user_id:
                return False
            
            await db.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            await db.commit()
            return True
    
    async def get_all_shared_rules(self) -> List[Dict]:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM rules WHERE shared = 1 ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ============================================================
    # 订单操作
    # ============================================================
    async def create_order(self, order_id: str, product_type: str,
                           customer_email: str, machine_id: str,
                           amount: float, checkout_url: str,
                           customer_name: str = None) -> int:
        async with self.get_connection() as db:
            cursor = await db.execute("""
                INSERT INTO orders (
                    order_id, product_type, customer_email, customer_name,
                    machine_id, amount, checkout_url, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, product_type, customer_email, customer_name,
                  machine_id, amount, checkout_url, 'pending'))
            await db.commit()
            return cursor.lastrowid
    
    async def get_order(self, order_id: str):
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM orders WHERE order_id = ?",
                (order_id,)
            )
            return await cursor.fetchone()
    
    async def get_order_by_lemon_id(self, lemon_order_id: str):
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM orders WHERE lemon_squeezy_order_id = ?",
                (lemon_order_id,)
            )
            return await cursor.fetchone()
    
    async def update_order_status(self, order_id: str, status: str,
                                   activation_code: str = None,
                                   lemon_order_id: str = None):
        async with self.get_connection() as db:
            await db.execute("""
                UPDATE orders SET 
                    status = ?,
                    activation_code = COALESCE(?, activation_code),
                    lemon_squeezy_order_id = COALESCE(?, lemon_squeezy_order_id),
                    paid_at = CASE WHEN ? = 'paid' THEN CURRENT_TIMESTAMP ELSE paid_at END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            """, (status, activation_code, lemon_order_id, status, order_id))
            await db.commit()
    
    async def get_user_orders(self, email: str) -> List[Dict]:
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM orders WHERE customer_email = ? ORDER BY created_at DESC",
                (email,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def list_orders(self, status: str = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        async with self.get_connection() as db:
            if status:
                cursor = await db.execute(
                    "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (status, limit, offset)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_order_stats(self) -> Dict:
        """获取订单统计数据"""
        async with self.get_connection() as db:
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_orders,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                    SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as total_revenue
                FROM orders
            """)
            row = await cursor.fetchone()
            return dict(row) if row else {
                'total_orders': 0, 'paid_orders': 0,
                'pending_orders': 0, 'total_revenue': 0
            }


# ===== 全局单例 =====
db = Database()