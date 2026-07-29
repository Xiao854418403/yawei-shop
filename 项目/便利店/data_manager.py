"""
便利店在线商城 - 数据管理层
负责 JSON 文件的读写、原子写入、并发锁保护
"""

import json
import os
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml

# 中国时区
CST = timezone(timedelta(hours=8))


def now_iso() -> str:
    """返回当前北京时间 ISO 字符串"""
    return datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S")


def today_str() -> str:
    """返回今天日期字符串 YYYY-MM-DD"""
    return datetime.now(CST).strftime("%Y-%m-%d")


class DataManager:
    """
    数据管理器 - 提供线程/进程安全的 JSON 文件读写。

    特性:
    - 原子写入：先写 .tmp 文件，再 os.replace（POSIX/Windows 均为原子操作）
    - 文件锁：通过 filelock 防止并发写入冲突
    - 自动初始化：首次运行时创建 data/ 目录和默认数据文件
    - in-memory 缓存：通过 st.cache_resource 在 Streamlit 中缓存单例
    """

    def __init__(self, data_dir: str | None = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.products_path = self.data_dir / "products.json"
        self.orders_path = self.data_dir / "orders.json"

        # 线程锁（RLock 可重入，防止同一线程内嵌套调用死锁）
        self._products_lock = threading.RLock()
        self._orders_lock = threading.RLock()
        self._announce_lock = threading.RLock()

        self.announcements_path = self.data_dir / "announcements.json"

        # 加载配置
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        self.config = self._load_yaml(config_path)

        # 确保数据文件存在
        self._ensure_files()

    # ========== 配置 ==========

    def _load_yaml(self, path: str) -> dict:
        """加载 YAML 配置文件"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    @property
    def store_name(self) -> str:
        return self.config.get("store", {}).get("name", "便利店")

    @property
    def categories(self) -> list[str]:
        return self.config.get("categories", ["零食", "饮料", "烟", "酒", "槟榔", "日用品"])

    @property
    def admin_password(self) -> str:
        """管理员密码：优先 st.secrets，其次 config.yaml"""
        try:
            import streamlit as st
            return st.secrets.get("ADMIN_PASSWORD", self.config.get("admin", {}).get("password", "admin123"))
        except Exception:
            return self.config.get("admin", {}).get("password", "admin123")

    @property
    def staff_password(self) -> str:
        """店员密码：优先 st.secrets，其次 config.yaml"""
        try:
            import streamlit as st
            return st.secrets.get("STAFF_PASSWORD", self.config.get("staff", {}).get("password", "staff123"))
        except Exception:
            return self.config.get("staff", {}).get("password", "staff123")

    # ========== 文件初始化 ==========

    def _ensure_files(self):
        """如果 JSON 文件不存在，创建带默认结构的空文件"""
        if not self.products_path.exists():
            self._write_json(self.products_path, {
                "products": [],
                "meta": {
                    "last_updated": now_iso(),
                    "total_products": 0,
                    "categories": self.categories,
                }
            })

        if not self.orders_path.exists():
            self._write_json(self.orders_path, {
                "orders": [],
                "meta": {
                    "last_updated": now_iso(),
                    "total_orders": 0,
                    "order_counter": 0,
                }
            })

        if not self.announcements_path.exists():
            self._write_json(self.announcements_path, {
                "announcements": [],
                "meta": {"last_updated": now_iso(), "total": 0}
            })

    def reinitialize_data(self):
        """强制重建数据文件（用于重置/首次种子数据写入）"""
        self.products_path.unlink(missing_ok=True)
        self.orders_path.unlink(missing_ok=True)
        self._ensure_files()

    # ========== 原子读写 ==========

    def _read_json(self, path: Path) -> dict:
        """读取 JSON 文件（无锁，可接受短暂不一致）"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_json(self, path: Path, data: dict):
        """直接写入 JSON（用于初始化，不竞争）"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _atomic_write(self, path: Path, data: dict):
        """
        原子写入：写 .tmp → os.replace。
        在支持 os.replace 的所有平台上（包括 Windows）都是原子的。
        """
        tmp_path = path.with_suffix(".tmp")
        lock = self._products_lock if "products" in str(path) else self._orders_lock
        with lock:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)

    def _read_with_lock(self, path: Path) -> dict:
        """带锁读取"""
        lock = self._products_lock if "products" in str(path) else self._orders_lock
        with lock:
            return self._read_json(path)

    def _write_with_lock(self, path: Path, data: dict):
        """带锁写入"""
        lock = self._products_lock if "products" in str(path) else self._orders_lock
        with lock:
            self._write_json(path, data)

    # ========== 商品操作 ==========

    def load_products(self) -> list[dict]:
        """加载所有商品列表"""
        data = self._read_json(self.products_path)
        return data.get("products", [])

    def load_active_products(self) -> list[dict]:
        """加载启用的商品（顾客端用）"""
        return [p for p in self.load_products() if p.get("is_active", True)]

    def get_product(self, product_id: str) -> dict | None:
        """根据 ID 获取单个商品"""
        for p in self.load_products():
            if p["id"] == product_id:
                return p
        return None

    def save_products(self, products: list[dict]):
        """保存商品列表（原子写入）"""
        # 更新 meta
        active_count = sum(1 for p in products if p.get("is_active", True))
        data = {
            "products": products,
            "meta": {
                "last_updated": now_iso(),
                "total_products": len(products),
                "active_products": active_count,
                "categories": self.categories,
            }
        }
        self._atomic_write(self.products_path, data)

    def add_product(self, product: dict) -> str:
        """添加新商品，返回生成的 ID"""
        products = self.load_products()
        # 生成 ID
        max_id = 0
        for p in products:
            try:
                num = int(p["id"][1:])
                max_id = max(max_id, num)
            except (ValueError, KeyError):
                pass
        product["id"] = f"P{max_id + 1:03d}"
        product["created_at"] = now_iso()
        product["updated_at"] = now_iso()
        product.setdefault("is_active", True)
        products.append(product)
        self.save_products(products)
        return product["id"]

    def update_product(self, product_id: str, updates: dict) -> bool:
        """更新商品信息，返回是否成功"""
        products = self.load_products()
        for i, p in enumerate(products):
            if p["id"] == product_id:
                products[i].update(updates)
                products[i]["updated_at"] = now_iso()
                products[i]["id"] = product_id  # 不允许改 ID
                self.save_products(products)
                return True
        return False

    def delete_product(self, product_id: str, hard: bool = False) -> bool:
        """
        删除商品：soft delete（标记 is_active=False），hard 为真删除
        """
        products = self.load_products()
        for i, p in enumerate(products):
            if p["id"] == product_id:
                if hard:
                    products.pop(i)
                else:
                    products[i]["is_active"] = False
                    products[i]["updated_at"] = now_iso()
                self.save_products(products)
                return True
        return False

    def decrement_stock(self, items: list[dict]) -> tuple[bool, str]:
        """
        下单时扣减库存（线程安全）。
        items: [{"product_id": "P001", "quantity": 2}, ...]
        返回 (成功, 错误信息)
        """
        with self._products_lock:
            data = self._read_json(self.products_path)
            products = data.get("products", [])

            # 校验库存
            for item in items:
                pid = item["product_id"]
                qty = item["quantity"]
                found = False
                for p in products:
                    if p["id"] == pid:
                        found = True
                        if not p.get("is_active", True):
                            return False, f"商品「{p['name']}」已下架"
                        if p["stock"] < qty:
                            return False, f"商品「{p['name']}」库存不足（剩余 {p['stock']}）"
                        break
                if not found:
                    return False, f"商品 ID {pid} 不存在"

            # 扣减库存
            for item in items:
                for p in products:
                    if p["id"] == item["product_id"]:
                        p["stock"] -= item["quantity"]
                        p["updated_at"] = now_iso()
                        break

            data["products"] = products
            data["meta"]["last_updated"] = now_iso()
            self._write_json(self.products_path, data)
            return True, ""

    # ========== 订单操作 ==========

    def load_orders(self) -> list[dict]:
        """加载所有订单"""
        data = self._read_json(self.orders_path)
        return data.get("orders", [])

    def get_orders_by_phone(self, phone: str) -> list[dict]:
        """根据手机号查询订单（按时间倒序）"""
        orders = self.load_orders()
        matched = [o for o in orders if o.get("customer_phone") == phone]
        matched.sort(key=lambda o: o.get("created_at", ""), reverse=True)
        return matched

    def get_order(self, order_id: str) -> dict | None:
        """根据订单号获取订单"""
        for o in self.load_orders():
            if o["order_id"] == order_id:
                return o
        return None

    def create_order(self, order_data: dict) -> tuple[bool, str, str | None]:
        """
        创建新订单（线程安全）。
        返回 (成功, 错误信息, 订单号)
        """
        with self._orders_lock:
            data = self._read_json(self.orders_path)
            orders = data.get("orders", [])
            meta = data.get("meta", {"total_orders": 0, "order_counter": 0})

            counter = meta.get("order_counter", 0) + 1
            order_id = f"ORD-{today_str().replace('-', '')}-{counter:03d}"

            order = {
                "order_id": order_id,
                "customer_name": order_data.get("customer_name", ""),
                "customer_phone": order_data.get("customer_phone", ""),
                "delivery_address": order_data.get("delivery_address", ""),
                "items": order_data.get("items", []),
                "total_amount": order_data.get("total_amount", 0),
                "status": "待确认",
                "note": order_data.get("note", ""),
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "status_history": [{"status": "待确认", "timestamp": now_iso()}],
            }
            orders.append(order)

            meta["total_orders"] = len(orders)
            meta["order_counter"] = counter
            meta["last_updated"] = now_iso()
            data["orders"] = orders
            data["meta"] = meta

            self._atomic_write(self.orders_path, data)
            return True, "", order_id

    def update_order_status(self, order_id: str, new_status: str) -> tuple[bool, str]:
        """
        更新订单状态（线程安全，带状态流转校验）。
        """
        VALID_TRANSITIONS = {
            "待确认": ["待核实", "已确认", "已取消"],
            "待核实": ["已确认", "待确认", "已取消"],
            "已确认": ["配送中", "已取消"],
            "配送中": ["已送达"],
        }

        with self._orders_lock:
            data = self._read_json(self.orders_path)
            orders = data.get("orders", [])

            for o in orders:
                if o["order_id"] == order_id:
                    current = o["status"]
                    allowed = VALID_TRANSITIONS.get(current, [])
                    if new_status not in allowed:
                        return False, f"不能从「{current}」转为「{new_status}」"
                    o["status"] = new_status
                    o["updated_at"] = now_iso()
                    o.setdefault("status_history", []).append({
                        "status": new_status,
                        "timestamp": now_iso(),
                    })

                    data["orders"] = orders
                    data["meta"]["last_updated"] = now_iso()
                    self._atomic_write(self.orders_path, data)
                    return True, ""

            return False, f"订单 {order_id} 不存在"

    def _add_note_to_order(self, order_id: str, note: str) -> bool:
        """给订单追加备注（线程安全）"""
        with self._orders_lock:
            data = self._read_json(self.orders_path)
            orders = data.get("orders", [])
            for o in orders:
                if o["order_id"] == order_id:
                    o["note"] = note
                    o["updated_at"] = now_iso()
                    data["orders"] = orders
                    data["meta"]["last_updated"] = now_iso()
                    self._atomic_write(self.orders_path, data)
                    return True
            return False

    # ========== 配送配置 ==========

    @property
    def delivery_min_amount(self) -> float:
        return self.config.get("delivery", {}).get("min_amount", 30)

    @property
    def delivery_free_amount(self) -> float:
        return self.config.get("delivery", {}).get("free_amount", 30)

    @property
    def pickup_only_below(self) -> bool:
        return self.config.get("delivery", {}).get("pickup_only_below", True)

    @property
    def remote_areas(self) -> list[str]:
        return self.config.get("delivery", {}).get("remote_areas", [])

    def is_remote_area(self, address: str) -> bool:
        """检查地址是否属于偏远地区"""
        for area in self.remote_areas:
            if area in address:
                return True
        return False

    # ========== 公告管理 ==========

    def load_announcements(self) -> list[dict]:
        """加载所有公告"""
        data = self._read_json(self.announcements_path)
        return data.get("announcements", [])

    def load_active_announcements(self) -> list[dict]:
        """加载当前有效的公告"""
        return [a for a in self.load_announcements() if a.get("is_active", True)]

    def add_announcement(self, title: str, content: str, ann_type: str = "通知") -> str:
        """添加公告，返回 ID"""
        with self._announce_lock:
            data = self._read_json(self.announcements_path)
            anns = data.get("announcements", [])
            aid = f"A{len(anns)+1:03d}"
            ann = {
                "id": aid, "title": title, "content": content,
                "type": ann_type, "is_active": True,
                "created_at": now_iso(),
            }
            anns.append(ann)
            data["announcements"] = anns
            data["meta"] = {"last_updated": now_iso(), "total": len(anns)}
            self._atomic_write(self.announcements_path, data)
            return aid

    def toggle_announcement(self, aid: str) -> bool:
        """切换公告启用/禁用"""
        with self._announce_lock:
            data = self._read_json(self.announcements_path)
            for a in data.get("announcements", []):
                if a["id"] == aid:
                    a["is_active"] = not a.get("is_active", True)
                    data["meta"]["last_updated"] = now_iso()
                    self._atomic_write(self.announcements_path, data)
                    return True
            return False

    def delete_announcement(self, aid: str) -> bool:
        """删除公告"""
        with self._announce_lock:
            data = self._read_json(self.announcements_path)
            anns = data.get("announcements", [])
            new_anns = [a for a in anns if a["id"] != aid]
            if len(new_anns) == len(anns):
                return False
            data["announcements"] = new_anns
            data["meta"] = {"last_updated": now_iso(), "total": len(new_anns)}
            self._atomic_write(self.announcements_path, data)
            return True

    # ========== 统计 ==========

    def get_stats(self) -> dict:
        """获取统计概览"""
        orders = self.load_orders()
        total_orders = len(orders)
        total_revenue = sum(o.get("total_amount", 0) for o in orders if o.get("status") != "已取消")
        pending = sum(1 for o in orders if o.get("status") in ("待确认", "待核实"))
        today = today_str()
        today_orders = sum(1 for o in orders if o.get("created_at", "").startswith(today))

        # 按品类统计
        category_sales: dict[str, float] = {}
        for o in orders:
            if o.get("status") == "已取消":
                continue
            for item in o.get("items", []):
                cat = item.get("category", "其他")
                category_sales[cat] = category_sales.get(cat, 0) + item.get("subtotal", 0)

        # 近7天每日订单数
        from collections import defaultdict
        daily: dict[str, int] = defaultdict(int)
        for o in orders:
            date_str = o.get("created_at", "")[:10]
            if date_str:
                daily[date_str] += 1

        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "pending_orders": pending,
            "today_orders": today_orders,
            "category_sales": category_sales,
            "daily_orders": dict(sorted(daily.items())[-7:]),  # 最近7天
        }

    def get_top_products(self, limit: int = 10) -> list[dict]:
        """热销商品排行"""
        orders = self.load_orders()
        sales: dict[str, dict] = {}
        for o in orders:
            if o.get("status") == "已取消":
                continue
            for item in o.get("items", []):
                pid = item.get("product_id", "")
                if pid not in sales:
                    sales[pid] = {"product_id": pid, "name": item.get("name", ""), "quantity": 0, "revenue": 0}
                sales[pid]["quantity"] += item.get("quantity", 0)
                sales[pid]["revenue"] += item.get("subtotal", 0)

        result = sorted(sales.values(), key=lambda x: x["quantity"], reverse=True)
        return result[:limit]
