"""
便利店在线商城 — Streamlit 主程序
小明便利店：零食 · 烟酒 · 槟榔 · 日用品
"""

import os
import sys
import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 确保可以导入同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 商品图标选择列表（60+ 图标按品类分组）
PRODUCT_EMOJIS = [
    # 零食
    "🍟 薯片", "🍪 饼干", "🥩 肉脯", "🌶️ 辣条", "🥜 坚果",
    "🍫 巧克力", "🍬 糖果", "🍭 棒棒糖", "🍩 甜甜圈", "🍿 爆米花",
    "🍘 锅巴", "🍞 面包", "🌮 零嘴", "🧁 蛋糕", "🍮 布丁",
    "🥟 粽子", "🍡 团子", "🍢 串串", "🍱 便当", "🥮 月饼",
    "🍠 烤红薯", "🌽 玉米", "🥐 牛角包", "🥨 椒盐卷饼",
    # 饮料
    "🥤 饮料", "🥃 可乐", "💧 矿泉水", "🫧 气泡水", "🍵 茶",
    "☕ 咖啡", "🧃 果汁", "🧋 奶茶", "🥛 牛奶", "🍶 白酒",
    "🫖 茶壶", "🍼 奶瓶", "🍯 蜂蜜",
    # 烟酒
    "🚬 香烟", "🍺 啤酒", "🍷 红酒", "🍹 鸡尾酒", "🍾 香槟",
    "🥂 干杯", "🍸 洋酒",
    # 槟榔
    "🫘 槟榔", "🫒 橄榄", "🌰 栗子",
    # 日用品
    "🧻 纸巾", "🧴 洗衣液", "🧼 洗手液", "🪥 牙膏", "🧹 扫把",
    "🧺 洗涤", "🪣 水桶", "🔋 电池", "🕯️ 蜡烛", "🧤 手套",
    "🪒 剃须刀", "🧦 袜子", "🩴 拖鞋",
    # 调味/食材
    "🧂 调味料", "🫙 罐头", "🧊 冰块", "🥚 鸡蛋", "🍚 米饭",
    "🍜 泡面", "🫕 火锅料", "🧀 奶酪", "🫒 橄榄油",
    # 其他
    "📦 其他", "🎁 礼品", "💊 药品", "🌯 卷饼", "🥪 三明治",
    "🍔 汉堡", "🍕 披萨", "🌭 热狗",
]

from data_manager import DataManager, now_iso
from seed_data import seed_products
from beep_data import BEEP_BASE64

# 应用根目录（比 __file__ 更可靠）
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="亚伟便利店_24小时",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 自定义 CSS（响应式 + 美化）
# ============================================================
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; }

    /* 全局柔光背景 */
    .main { background: linear-gradient(180deg, #faf7ff 0%, #f5f0ff 30%, #f0f4ff 100%) !important; }
    .stApp { background: transparent !important; }

    .store-title {
        font-size: 1.8rem; font-weight: 700;
        background: linear-gradient(135deg, #7c3aed, #8b5cf6, #6366f1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.1rem; letter-spacing: 1px;
    }
    .store-subtitle {
        font-size: 0.8rem; color: #a78bfa; text-align: center; margin-bottom: 1.5rem;
        letter-spacing: 2px;
    }

    /* 商品卡片 — 磨砂玻璃 */
    .product-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border-radius: 16px; padding: 1.4rem 1rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(139,92,246,0.06), 0 0 0 1px rgba(139,92,246,0.04);
        text-align: center; transition: all 0.3s ease;
        border: none; position: relative; overflow: hidden;
    }
    .product-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #a78bfa, #8b5cf6, #6366f1);
        opacity: 0; transition: opacity 0.3s;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(139,92,246,0.12), 0 0 0 1px rgba(139,92,246,0.1);
        background: rgba(255,255,255,0.9);
    }
    .product-card:hover::before { opacity: 1; }
    .product-emoji { font-size: 2.8rem; margin-bottom: 0.4rem; }
    .product-name { font-size: 0.95rem; font-weight: 600; color: #3b2f5c; margin-bottom: 0.2rem; }
    .product-desc { font-size: 0.75rem; color: #b4a5d6; margin-bottom: 0.5rem; }
    .product-price {
        font-size: 1.35rem; font-weight: 700;
        color: #7c3aed; margin-bottom: 0.1rem;
    }
    .product-stock { font-size: 0.7rem; color: #c4b5e8; margin-bottom: 0.6rem; }
    .product-stock.low { color: #ef4444; font-weight: 600; }

    /* 品类标签 */
    .category-badge {
        display: inline-block; padding: 0.15rem 0.7rem; border-radius: 20px;
        font-size: 0.7rem; font-weight: 500; margin-bottom: 0.4rem;
    }
    .cat-零食 { background: rgba(251,191,36,0.12); color: #b45309; }
    .cat-饮料 { background: rgba(99,102,241,0.1); color: #4f46e5; }
    .cat-烟   { background: rgba(239,68,68,0.08); color: #b91c1c; }
    .cat-酒   { background: rgba(139,92,246,0.1); color: #7c3aed; }
    .cat-槟榔 { background: rgba(34,197,94,0.1); color: #15803d; }
    .cat-日用品 { background: rgba(236,72,153,0.08); color: #be185d; }

    /* 状态标签 */
    .status-badge {
        display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600;
    }
    .status-待确认 { background: rgba(251,191,36,0.15); color: #a16207; }
    .status-待核实 { background: rgba(139,92,246,0.12); color: #7c3aed; }
    .status-已确认 { background: rgba(99,102,241,0.1); color: #4f46e5; }
    .status-配送中 { background: rgba(34,197,94,0.12); color: #15803d; }
    .status-已送达 { background: rgba(148,163,184,0.1); color: #64748b; }
    .status-已取消 { background: rgba(239,68,68,0.1); color: #b91c1c; }

    /* 订单卡片 */
    .order-card {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(8px);
        border-radius: 14px; padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem; border: 1px solid rgba(139,92,246,0.06);
        box-shadow: 0 2px 8px rgba(139,92,246,0.03);
    }

    /* KPI 卡片 */
    .kpi-card {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(8px);
        border-radius: 14px; padding: 1.5rem 1rem; text-align: center;
        box-shadow: 0 2px 10px rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.05);
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #5b3cc4; }
    .kpi-label { font-size: 0.8rem; color: #a78bfa; margin-top: 0.3rem; font-weight: 500; }
    .kpi-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }

    /* 按钮 — 紫罗兰主色 */
    div.stButton > button {
        border-radius: 10px !important; font-weight: 500 !important;
        transition: all 0.25s !important; border: none !important;
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
        color: #fff !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
        box-shadow: 0 4px 16px rgba(139,92,246,0.3) !important;
        transform: translateY(-1px);
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(139,92,246,0.08) !important; color: #7c3aed !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: rgba(139,92,246,0.14) !important;
    }

    /* 公告横幅 */
    .announce-banner {
        background: rgba(139,92,246,0.06);
        border-left: 4px solid #8b5cf6; border-radius: 10px;
        padding: 0.8rem 1.2rem; margin-bottom: 1rem;
        font-size: 0.9rem; color: #6d28d9;
    }
    .announce-banner.promo {
        background: rgba(251,191,36,0.08); border-left-color: #f59e0b; color: #92400e;
    }
    .announce-banner.urgent {
        background: rgba(239,68,68,0.06); border-left-color: #ef4444; color: #991b1b;
    }

    /* 侧边栏 — 轻盈紫白 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(250,247,255,0.95) 0%, rgba(245,240,255,0.95) 50%, rgba(240,244,255,0.95) 100%) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(139,92,246,0.08);
    }
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 10px !important; font-size: 0.85rem !important;
        background: rgba(139,92,246,0.07) !important; color: #7c3aed !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(139,92,246,0.14) !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important; color: #fff !important;
    }

    /* 表单 */
    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(8px);
        border-radius: 14px; padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.06);
    }
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
        color: #fff !important; font-size: 1rem !important;
    }

    @media (max-width: 768px) {
        .store-title { font-size: 1.4rem; }
        .product-emoji { font-size: 2.2rem; }
        .product-price { font-size: 1.1rem; }
        .product-card { padding: 1rem 0.6rem; border-radius: 14px; }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 初始化
# ============================================================

@st.cache_resource
def get_dm() -> DataManager:
    """缓存 DataManager 单例"""
    return DataManager()


def init_session_state():
    """初始化所有 session_state 键"""
    defaults = {
        "role": "customer",          # customer | staff | admin
        "cart": {},                  # {product_id: {name, price, quantity, emoji, category}}
        "admin_authenticated": False,
        "staff_authenticated": False,
        "selected_category": "全部",
        "search_query": "",
        "order_phone": "",
        "checkout_submitted": False,
        "customer_page": "🏪 商品浏览",  # 顾客端当前页面
        "_nav_programmatic": False,     # 标记是否由按钮触发导航
        "_last_order_id": None,          # 最近下单的订单号
        "_last_order_phone": "",         # 最近下单的手机号
        "_payment_order_id": None,        # 待付款订单号
        "_payment_amount": 0,             # 待付款金额
        "_last_seen_order_count": 0,      # 上次看到的待确认订单数
        "_checkout_done": False,           # 下单成功标记
        "_payment_done": False,            # 付款确认完成标记
        "customer_logged_in": False,       # 顾客是否已登录
        "customer_phone": "",              # 已登录顾客手机号
        "_verify_code": "",                # 生成的验证码
        "_verify_phone": "",               # 验证码对应的手机号
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# 首次运行：初始化数据
dm = get_dm()
if not dm.load_products():
    seed_products()

init_session_state()


# ============================================================
# 工具函数
# ============================================================

def get_cart_count() -> int:
    """购物车总件数"""
    return sum(item["quantity"] for item in st.session_state.cart.values())


def get_cart_total() -> float:
    """购物车总金额"""
    return sum(item["price"] * item["quantity"] for item in st.session_state.cart.values())


def add_to_cart(product: dict):
    """添加商品到购物车"""
    cart = st.session_state.cart
    pid = product["id"]
    if pid in cart:
        cart[pid]["quantity"] += 1
    else:
        cart[pid] = {
            "product_id": pid,
            "name": product["name"],
            "price": product["price"],
            "quantity": 1,
            "emoji": product.get("image_emoji", "📦"),
            "category": product.get("category", ""),
        }


def remove_from_cart(product_id: str):
    """从购物车移除商品"""
    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]


def clear_cart():
    """清空购物车"""
    st.session_state.cart = {}


def format_price(price: float) -> str:
    """格式化价格"""
    return f"¥{price:.2f}"


# ============================================================
# 侧边栏
# ============================================================

def render_sidebar():
    """渲染全局侧边栏"""
    with st.sidebar:
        store_cfg = dm.config.get("store", {})
        st.markdown(f'<div class="store-title">🏪 {dm.store_name}</div>', unsafe_allow_html=True)
        if store_cfg.get("subtitle"):
            st.markdown(f'<div class="store-subtitle">{store_cfg["subtitle"]}</div>', unsafe_allow_html=True)

        st.divider()

        # 角色切换
        role_labels = {"customer": "🧑 顾客购物", "staff": "👷 店员后台", "admin": "🔧 管理员"}
        current_role_idx = {"customer": 0, "staff": 1, "admin": 2}.get(st.session_state.role, 0)
        st.session_state.role = st.radio(
            "选择身份",
            options=["customer", "staff", "admin"],
            format_func=lambda x: role_labels[x],
            index=current_role_idx,
            key="role_radio",
            horizontal=True,
        )

        st.divider()

        # 顾客模式：页面导航 + 购物车摘要
        if st.session_state.role == "customer":
            if st.session_state.customer_logged_in:
                st.success(f"📱 {st.session_state.customer_phone}")
                if st.button("🚪 退出登录", use_container_width=True, key="logout_btn"):
                    st.session_state.customer_logged_in = False
                    st.session_state.customer_phone = ""
                    st.session_state.cart = {}
                    st.rerun()
            else:
                st.info("👆 请先登录")

            st.divider()
            st.markdown("### 📋 菜单导航")

            cart_count = get_cart_count()
            pages = ["🏪 商品浏览", "🛒 购物车", "📋 下单结算", "💳 扫码付款", "📦 我的订单"]
            for pg in pages:
                is_current = (st.session_state.customer_page == pg)
                btn_style = "primary" if is_current else "secondary"
                label = pg
                if pg == "🛒 购物车" and cart_count > 0:
                    label = f"🛒 购物车 ({cart_count}件)"
                if st.button(label, key=f"nav_{pg}", use_container_width=True, type=btn_style):
                    st.session_state.customer_page = pg
                    st.rerun()

            if cart_count > 0:
                cart_total = get_cart_total()
                st.markdown(f"**💰 合计：{format_price(cart_total)}**")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🛍️ 去结算", use_container_width=True):
                        st.session_state.customer_page = "📋 下单结算"
                        st.rerun()
                with col2:
                    if st.button("🗑️ 清空", use_container_width=True):
                        clear_cart()
                        st.rerun()
            else:
                st.caption("🛒 购物车为空")

            st.divider()
            st.caption(f"📞 店铺电话：{store_cfg.get('phone', 'N/A')}")
            st.caption(f"🚀 {store_cfg.get('delivery_note', '')}")

        # 店员模式
        elif st.session_state.role == "staff":
            if st.session_state.staff_authenticated:
                st.success("👷 店员已登录")
                if st.button("🚪 退出登录", use_container_width=True):
                    st.session_state.staff_authenticated = False
                    st.rerun()

        # 管理员模式
        else:
            if st.session_state.admin_authenticated:
                st.success("🔧 管理员已登录")
                if st.button("🚪 退出登录", use_container_width=True):
                    st.session_state.admin_authenticated = False
                    st.rerun()


# ============================================================
# 顾客端 — 页面路由
# ============================================================

def render_customer():
    """根据侧边栏选择渲染顾客端页面"""
    if not st.session_state.customer_logged_in:
        render_login()
        return

    # 有未完成的付款 → 直接显示付款页，不受侧边栏导航影响
    if st.session_state.get("_payment_order_id"):
        render_payment()
        return

    page = st.session_state.customer_page

    if page == "🏪 商品浏览":
        render_product_catalog()
    elif page == "🛒 购物车":
        render_cart()
    elif page == "📋 下单结算":
        render_checkout()
    elif page == "💳 扫码付款":
        render_payment()
    elif page == "📦 我的订单":
        render_my_orders()


# ============================================================
# 顾客端 — 手机号登录
# ============================================================

def render_login():
    """手机号 + 验证码登录"""
    st.markdown("### 📱 欢迎光临")

    # 如果没有登录，显示登录入口
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ede4ff 0%, #e0d9ff 25%, #dbe4ff 60%, #e8f0ff 100%);
            border-radius: 20px; padding: 3rem 2rem; text-align: center;
            box-shadow: 0 4px 24px rgba(139,92,246,0.1);
            color: #3b2f5c; min-height: 360px; display: flex; flex-direction: column;
            justify-content: center; position: relative; overflow: hidden;
        ">
            <div style=\"position:absolute;top:-30px;right:-30px;width:140px;height:140px;background:rgba(139,92,246,0.06);border-radius:50%;\"></div>
            <div style=\"position:absolute;bottom:-20px;left:-20px;width:90px;height:90px;background:rgba(99,102,241,0.04);border-radius:50%;\"></div>
            <div style=\"position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,rgba(139,92,246,0.06) 0%,transparent 70%);\"></div>
            <div style="font-size:4.5rem; margin-bottom:1rem; position:relative; z-index:1; filter: drop-shadow(0 4px 8px rgba(139,92,246,0.15));">🏪</div>
            <div style="font-size:2rem; font-weight:700; margin-bottom:0.5rem; letter-spacing:2px; position:relative; z-index:1; color: #4c2d8f;">亚伟便利店_24小时</div>
            <div style="font-size:0.9rem; color:#8b6fc0; margin-bottom:0.3rem; position:relative; z-index:1; letter-spacing:1px;">
                ✨ 精选零食 · 烟酒 · 槟榔 · 日用
            </div>
            <div style="font-size:0.8rem; color:#a78bfa; margin-top:0.5rem; position:relative; z-index:1;">
                🚀 满30元配送到家 · 下单即送 · 品质保证
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style="text-align:center; margin-bottom:1rem;">
            <div style="font-size:1.3rem; font-weight:700; color:#1d1d1f;">🔐 手机号登录</div>
            <div style="font-size:0.85rem; color:#86868b;">登录后即可下单和查看订单</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            phone = st.text_input("手机号码", placeholder="请输入11位手机号", max_chars=11, key="login_phone")

            col_btn, col_code = st.columns([2, 1])
            with col_btn:
                send_clicked = st.form_submit_button("📩 获取验证码", use_container_width=True)
            with col_code:
                verify_input = st.text_input("验证码", placeholder="6位", max_chars=6, key="login_code")

            login_clicked = st.form_submit_button("🔓 登录", type="primary", use_container_width=True)

            if send_clicked:
                if not phone or not phone.isdigit() or len(phone) != 11:
                    st.error("请输入正确的11位手机号")
                else:
                    code = str(random.randint(100000, 999999))
                    st.session_state._verify_code = code
                    st.session_state._verify_phone = phone
                    st.success(f"验证码：**{code}**（模拟短信）")
                    st.caption("📱 部署后接入阿里云/腾讯云短信服务即可真实发送")

            if login_clicked:
                saved_code = st.session_state.get("_verify_code", "")
                saved_phone = st.session_state.get("_verify_phone", "")
                if not verify_input:
                    st.error("请输入验证码")
                elif verify_input != saved_code or phone != saved_phone:
                    st.error("验证码错误，请重新获取")
                else:
                    st.session_state.customer_logged_in = True
                    st.session_state.customer_phone = phone
                    st.session_state._verify_code = ""
                    st.session_state._verify_phone = ""
                    st.success(f"登录成功！欢迎 {phone}")
                    st.rerun()


# ============================================================
# 顾客端 — 商品浏览
# ============================================================

def render_product_catalog():
    """商品浏览页"""
    products = dm.load_active_products()

    # 店铺招牌横幅 — 横向铺满
    banner_path = os.path.join(APP_DIR, "data", "images", "shop_banner.png")
    if os.path.exists(banner_path):
        b64 = img_to_base64(banner_path)
        if b64:
            st.markdown(f'<div style="margin:-1rem -1rem 0 -1rem;"><img src="{b64}" style="width:100%;display:block;"></div>', unsafe_allow_html=True)

    # 公告横幅（滚动）
    announcements = dm.load_active_announcements()
    if announcements:
        items_html = ""
        for ann in announcements:
            icon = {"促销": "🎉", "紧急": "🔴", "通知": "📢"}.get(ann.get("type", ""), "📢")
            items_html += f'<span style="margin-right:3rem;">{icon} <strong>{ann["title"]}</strong> — {ann["content"]}</span>'
        st.markdown(f"""
        <div style="background:linear-gradient(90deg,#fef3c7,#fff7ed,#fef3c7);border-radius:8px;
        padding:0.6rem 1rem;margin-bottom:1rem;overflow:hidden;white-space:nowrap;">
            <marquee scrollamount="4" behavior="scroll" onmouseover="this.stop()" onmouseout="this.start()">
                {items_html}
            </marquee>
        </div>
        """, unsafe_allow_html=True)

    categories = ["全部"] + dm.categories

    # 品类筛选
    st.markdown("### 🔍 筛选商品")
    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            is_active = st.session_state.selected_category == cat
            btn_type = "primary" if is_active else "secondary"
            if st.button(cat, key=f"cat_{cat}", type=btn_type, use_container_width=True):
                st.session_state.selected_category = cat
                st.rerun()

    # 搜索
    search = st.text_input("🔍 搜索商品", placeholder="输入商品名称...", key="search_input",
                           value=st.session_state.search_query)
    st.session_state.search_query = search

    st.divider()

    # 筛选
    filtered = products
    sel_cat = st.session_state.selected_category
    if sel_cat != "全部":
        filtered = [p for p in filtered if p["category"] == sel_cat]
    if search.strip():
        filtered = [p for p in filtered if search.strip().lower() in p["name"].lower()
                     or search.strip().lower() in p.get("description", "").lower()]

    # 商品网格
    if not filtered:
        st.info("😕 没有找到匹配的商品，试试其他筛选条件吧")
        return

    st.markdown(f"共 **{len(filtered)}** 件商品")
    cols_per_row = 4
    for i in range(0, len(filtered), cols_per_row):
        row_items = filtered[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, product in enumerate(row_items):
            with cols[j]:
                render_product_card(product)


def img_to_base64(path: str) -> str:
    """将本地图片转为 base64 data URI"""
    import base64
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = path.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{data}"
    except Exception:
        return ""


def render_product_card(product: dict):
    """单个商品卡片"""
    name = product["name"]
    price = product["price"]
    stock = product["stock"]
    category = product.get("category", "")
    desc = product.get("description", "")
    pid = product["id"]
    unit = product.get("unit", "件")
    image_url = product.get("image_url", "")
    image_file = product.get("image_file", "")
    emoji = product.get("image_emoji", "📦")

    stock_class = "low" if stock <= 5 else ""

    # 图片：本地文件 > base64 > URL > emoji
    img_html = ""
    if image_file:
        local_path = os.path.join(APP_DIR, "data", "images", image_file)
        if os.path.exists(local_path):
            b64 = img_to_base64(local_path)
            if b64:
                img_html = f'<img src="{b64}" style="width:100%;height:140px;object-fit:cover;border-radius:10px;margin-bottom:0.5rem;">'
    if not img_html and image_url:
        img_html = f'<img src="{image_url}" style="width:100%;height:140px;object-fit:cover;border-radius:10px;margin-bottom:0.5rem;" onerror="this.style.display=\'none\'">'
    if not img_html:
        img_html = f'<div class="product-emoji">{emoji}</div>'

    html = f"""
    <div class="product-card">
        {img_html}
        <span class="category-badge cat-{category}">{category}</span>
        <div class="product-name">{name}</div>
        <div class="product-desc">{desc}</div>
        <div class="product-price">¥{price:.2f}<small style="font-size:0.8rem">/{unit}</small></div>
        <div class="product-stock {stock_class}">库存：{stock}{unit}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # 加入购物车按钮
    if stock > 0:
        cart = st.session_state.cart
        in_cart = pid in cart
        btn_label = f"🛒 加入购物车 ({cart[pid]['quantity']}件)" if in_cart else "🛒 加入购物车"
        if st.button(btn_label, key=f"add_{pid}", use_container_width=True):
            add_to_cart(product)
            st.success(f"{name} 已加入购物车")
            st.rerun()
    else:
        st.button("暂 时 缺 货", key=f"oos_{pid}", disabled=True, use_container_width=True)


# ============================================================
# 顾客端 — 购物车
# ============================================================

def render_cart():
    """购物车页"""
    cart = st.session_state.cart

    if not cart:
        st.info("🛒 购物车还是空的，去逛逛吧~")
        return

    st.markdown("### 🛒 我的购物车")

    # 购物车表格
    rows = []
    for pid, item in cart.items():
        rows.append({
            "商品": f"{item['emoji']} {item['name']}",
            "单价": format_price(item["price"]),
            "数量": item["quantity"],
            "小计": format_price(item["price"] * item["quantity"]),
            "操作": pid,
        })

    for i, row in enumerate(rows):
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1.5, 1, 1])
        with col1:
            st.markdown(f"**{row['商品']}**")
        with col2:
            st.markdown(row["单价"])
        with col3:
            qty_col1, qty_col2, qty_col3 = st.columns([0.5, 0.8, 0.5])
            with qty_col1:
                if st.button("➖", key=f"dec_{row['操作']}"):
                    cart[row["操作"]]["quantity"] -= 1
                    if cart[row["操作"]]["quantity"] <= 0:
                        del cart[row["操作"]]
                    st.rerun()
            with qty_col2:
                st.markdown(f"**{row['数量']}**")
            with qty_col3:
                inc_disabled = False
                # Check if adding more would exceed stock
                product = dm.get_product(row['操作'])
                if product and cart[row['操作']]["quantity"] >= product["stock"]:
                    inc_disabled = True
                if st.button("➕", key=f"inc_{row['操作']}", disabled=inc_disabled):
                    cart[row["操作"]]["quantity"] += 1
                    st.rerun()
        with col4:
            st.markdown(f"**{row['小计']}**")
        with col5:
            if st.button("🗑️", key=f"del_{row['操作']}"):
                remove_from_cart(row["操作"])
                st.rerun()

    st.divider()
    total = get_cart_total()
    count = get_cart_count()
    st.markdown(f"### 💰 合计：**{format_price(total)}**（共 {count} 件）")

    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("🗑️ 清空购物车", type="secondary", use_container_width=True):
            clear_cart()
            st.rerun()
    with col_b:
        if st.button("📋 去结算", type="primary", use_container_width=True):
            st.session_state.customer_page = "📋 下单结算"
            st.session_state["_nav_programmatic"] = True
            st.rerun()


# ============================================================
# 顾客端 — 下单结算
# ============================================================

def render_checkout():
    cart = st.session_state.cart
    st.markdown("### 📋 下单结算")
    if not cart:
        st.info("购物车为空")
        return

    total = get_cart_total()
    for item in cart.values():
        st.markdown(f"- {item['emoji']} {item['name']} x{item['quantity']} = {format_price(item['price']*item['quantity'])}")
    delivery_min = dm.delivery_min_amount
    can_deliver = total >= delivery_min

    st.markdown(f"**合计: {format_price(total)}**")
    st.divider()

    # 配送规则提示
    if not can_deliver:
        st.warning(f"⚠️ 订单金额 ¥{total:.2f} 不足 ¥{delivery_min}，仅支持**到店自提**。再加 ¥{delivery_min - total:.2f} 即可配送到家！")

    st.markdown("#### 🚀 收货信息")
    if can_deliver:
        delivery_mode = st.radio("配送方式", ["🚀 配送到家", "🏪 到店自提"], horizontal=True)
    else:
        delivery_mode = "🏪 到店自提"

    is_remote = False

    with st.form("checkout_form", clear_on_submit=False):
        name = st.text_input("收货人姓名 *", key="chk_name")
        phone = st.text_input("手机号码 *", value=st.session_state.get("customer_phone", ""), key="chk_phone")

        if delivery_mode == "🚀 配送到家":
            addr = st.text_input("配送地址 *", key="chk_addr")
            a_val = st.session_state.get("chk_addr", "")
            if a_val and dm.is_remote_area(a_val):
                st.error("⚠️ 该地址属于偏远地区，暂不支持配送，请选择自提")
                is_remote = True
        else:
            addr = st.text_input("取货方式", value="到店自提", disabled=True, key="chk_addr")

        note = st.text_input("备注", key="chk_note")
        ok = st.form_submit_button("确认下单", type="primary", use_container_width=True)

        if ok:
            n = st.session_state.get("chk_name", "").strip()
            p = st.session_state.get("chk_phone", "").strip()
            a = st.session_state.get("chk_addr", "").strip()
            nt = st.session_state.get("chk_note", "").strip()
            if is_remote:
                st.error("偏远地区不支持配送，请选择自提")
            elif not n or not p or not a:
                st.error("请填写姓名、手机号、地址")
            elif not p.isdigit() or len(p) != 11:
                st.error("手机号格式错误")
            else:
                try:
                    items = [{"product_id": v["product_id"], "quantity": v["quantity"]} for v in cart.values()]
                    ok1, err1 = dm.decrement_stock(items)
                    if not ok1:
                        st.error(f"库存: {err1}")
                    else:
                        order_items = [{
                            "product_id": v["product_id"], "name": v["name"], "price": v["price"],
                            "quantity": v["quantity"], "subtotal": round(v["price"]*v["quantity"],2),
                            "category": v.get("category",""), "emoji": v.get("emoji","📦"),
                        } for v in cart.values()]
                        ok2, err2, oid = dm.create_order({
                            "customer_name": n, "customer_phone": p, "delivery_address": a,
                            "items": order_items, "total_amount": round(total,2),
                            "note": nt,
                        })
                        if not ok2:
                            st.error(f"订单: {err2}")
                        else:
                            clear_cart()
                            st.session_state["_payment_order_id"] = oid
                            st.session_state["_payment_amount"] = round(total,2)
                            st.session_state["_last_order_id"] = oid
                            st.session_state["_last_order_phone"] = p
                            st.success(f"下单成功! 订单号: {oid}，应付: {format_price(round(total,2))}")
                            st.rerun()
                except Exception as e:
                    st.error(f"异常: {e}")


def render_payment():
    """扫码付款页"""
    st.markdown("### 💳 扫码付款")

    order_id = st.session_state.get("_payment_order_id", "")
    amount = st.session_state.get("_payment_amount", 0)

    # 有订单时显示金额卡片
    if order_id:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e74c3c,#c0392b);border-radius:16px;padding:1.5rem;text-align:center;color:white;margin-bottom:1.5rem;">
            <div style="font-size:0.9rem;opacity:0.9;">应付金额</div>
            <div style="font-size:2.8rem;font-weight:700;">¥{amount:.2f}</div>
            <div style="font-size:0.85rem;opacity:0.8;margin-top:0.5rem;">订单号：{order_id}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 请先在「📋 下单结算」中下单，下单后会自动跳转到此页面")

    # 始终显示二维码（双码：微信 + 支付宝）
    qr_wechat = os.path.join(APP_DIR, "data", "payment_qr_wechat.png")
    qr_alipay = os.path.join(APP_DIR, "data", "payment_qr_alipay.png")
    # 兼容旧版单码
    qr_old = os.path.join(APP_DIR, "data", "payment_qr.png")
    has_wechat = os.path.exists(qr_wechat) or os.path.exists(qr_old)
    has_alipay = os.path.exists(qr_alipay)

    if has_wechat or has_alipay:
        st.markdown("#### 📱 请选择扫码方式付款")
        if has_wechat and has_alipay:
            col_wx, col_ali = st.columns(2)
            with col_wx:
                st.markdown("**💚 微信支付**")
                wx_path = qr_wechat if os.path.exists(qr_wechat) else qr_old
                st.image(wx_path, caption="扫一扫付款", use_container_width=True)
            with col_ali:
                st.markdown("**💙 支付宝**")
                st.image(qr_alipay, caption="扫一扫付款", use_container_width=True)
        elif has_wechat:
            st.markdown("**💚 微信支付**")
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                wx_path = qr_wechat if os.path.exists(qr_wechat) else qr_old
                st.image(wx_path, caption="扫一扫付款", use_container_width=True)
        else:
            st.markdown("**💙 支付宝**")
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                st.image(qr_alipay, caption="扫一扫付款", use_container_width=True)

        st.caption("💡 付款时请输入订单显示的金额，店主收到到账通知后将确认您的订单")
    else:
        st.warning("⚠️ 收款二维码尚未设置，请联系店主上传收款码")

    if order_id:
        st.divider()
        st.markdown("#### 🔐 付款确认")
        st.warning("""
        ⚠️ **付款后请如实填写下方金额，店主会核对手机上的微信/支付宝到账记录。**
        如果金额对不上，订单将不会被确认。
        """)

        with st.form("payment_confirm_form", clear_on_submit=False):
            paid_amount = st.number_input(
                "请输入您实际支付的金额（元）",
                min_value=0.0,
                max_value=99999.0,
                value=float(amount),
                step=0.01,
                format="%.2f",
            )
            confirm_submitted = st.form_submit_button("✅ 我已完成付款，通知店主", type="primary", use_container_width=True)

            if confirm_submitted:
                if paid_amount <= 0:
                    st.error("请输入有效的支付金额")
                    st.stop()

                # 记录顾客声称的付款金额，状态改为"待核实"
                if abs(paid_amount - amount) > 0.01:
                    payment_note = f"[顾客声称已付 ¥{paid_amount:.2f}，与订单 ¥{amount:.2f} 不符，请核实手机到账记录]"
                else:
                    payment_note = f"[顾客声称已付 ¥{paid_amount:.2f}，金额一致，请核实手机到账记录]"

                dm._add_note_to_order(order_id, payment_note)
                # 状态改为"待核实"，等待店主审核
                dm.update_order_status(order_id, "待核实")

                st.session_state._payment_order_id = None
                st.session_state.customer_page = "📦 我的订单"
                st.session_state["_nav_programmatic"] = True
                st.success("已通知店主！请等待店主核对到账记录后确认订单")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            pass
        with col_btn2:
            if st.button("📋 跳过，查看我的订单", use_container_width=True):
                st.session_state._payment_order_id = None
                st.session_state.customer_page = "📦 我的订单"
                st.session_state["_nav_programmatic"] = True
                st.rerun()



# ============================================================
# 顾客端 — 我的订单
# ============================================================

def render_my_orders():
    """我的订单页"""
    st.markdown("### 📦 我的订单")

    # 如果刚从下单页跳过来，自动填入手机号并显示成功提示
    last_phone = st.session_state.get("_last_order_phone", "")
    last_order_id = st.session_state.get("_last_order_id", "")
    if last_order_id:
        st.success(f"🎉 下单成功！订单编号：**{last_order_id}**，我们将尽快为您配送")
        st.session_state._last_order_id = None  # 只显示一次

    phone = st.text_input("📱 请输入下单时填写的手机号", placeholder="13800138000",
                          max_chars=11, key="order_phone_input",
                          value=last_phone or st.session_state.customer_phone)

    if not phone:
        st.info("👆 输入手机号即可查询订单")
        return

    if not phone.isdigit() or len(phone) != 11:
        st.warning("请输入11位手机号码")
        return

    orders = dm.get_orders_by_phone(phone)

    if not orders:
        st.info("😕 该手机号暂无订单记录")
        return

    st.markdown(f"共找到 **{len(orders)}** 笔订单")
    st.divider()

    for order in orders:
        render_order_card(order)


def render_order_card(order: dict):
    """渲染单个订单卡片"""
    status = order.get("status", "未知")
    order_id = order.get("order_id", "")
    total = order.get("total_amount", 0)
    created = order.get("created_at", "")[:16].replace("T", " ")
    address = order.get("delivery_address", "")
    items = order.get("items", [])
    history = order.get("status_history", [])
    note = order.get("note", "")

    with st.container():
        st.markdown(f"""
        <div class="order-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                <div>
                    <strong style="font-size:1.05rem;">📋 {order_id}</strong>
                    <span style="color:#95a5a6;font-size:0.8rem;margin-left:1rem;">{created}</span>
                </div>
                <span class="status-badge status-{status}">{status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 商品明细
        st.markdown("**商品明细：**")
        for item in items:
            emoji = item.get("emoji", "📦")
            name = item.get("name", "")
            qty = item.get("quantity", 0)
            subtotal = item.get("subtotal", 0)
            st.markdown(f"  {emoji} {name} ×{qty} — {format_price(subtotal)}")

        st.markdown(f"**💰 订单金额：{format_price(total)}**")
        if note and "顾客声称已付" in note:
            st.info(f"💬 {note}")
        elif note:
            st.markdown(f"💬 备注：{note}")
        st.markdown(f"📍 地址：{address}")

        # 状态时间线
        if history:
            with st.expander("📋 订单轨迹"):
                for h in history:
                    ts = h.get("timestamp", "")[:16].replace("T", " ")
                    s = h.get("status", "")
                    st.markdown(f"- {ts} → <span class='status-badge status-{s}'>{s}</span>", unsafe_allow_html=True)

        st.divider()


# ============================================================
# 后台管理 — 密码验证
# ============================================================

def render_admin_login():
    """管理员登录门"""
    st.markdown("### 🔐 管理员登录")
    with st.form("admin_login_form"):
        pwd = st.text_input("请输入管理密码", type="password", placeholder="输入密码...")
        submitted = st.form_submit_button("登录", type="primary", use_container_width=True)
        if submitted:
            if pwd == dm.admin_password:
                st.session_state.admin_authenticated = True
                st.success("✅ 登录成功！")
            else:
                st.error("❌ 密码错误")


def render_admin_panel():
    """后台管理主页"""
    if not st.session_state.admin_authenticated:
        render_admin_login()
        return

    st.markdown("### 🔧 管理后台")

    admin_tabs = st.tabs(["📦 商品管理", "📋 订单管理", "📊 数据统计", "📢 公告管理"])

    with admin_tabs[0]:
        render_admin_products()
    with admin_tabs[1]:
        render_admin_orders()
    with admin_tabs[2]:
        render_admin_analytics()
    with admin_tabs[3]:
        render_admin_announcements()


# ============================================================
# 后台管理 — 商品管理
# ============================================================

def render_admin_products():
    """商品管理页"""
    st.markdown("#### 📦 商品管理")

    # 批量导入图片
    with st.expander("📷 批量导入商品图片", expanded=False):
        st.markdown("""
        **使用方法**：
        1. 把商品图片命名为商品 ID（如 `P001.jpg`、`P002.png`）
        2. 全部拖入下方上传框
        3. 系统自动匹配到对应商品
        """)
        batch_files = st.file_uploader("选择图片", type=["png", "jpg", "jpeg", "webp"],
                                       accept_multiple_files=True, key="batch_upload")
        if batch_files and st.button("开始批量导入", use_container_width=True):
            imported = 0
            for f in batch_files:
                pid = os.path.splitext(f.name)[0].upper()
                from data_manager import DataManager as DM2
                dm2 = DM2()
                products = dm2.load_products()
                for p in products:
                    if p["id"].upper() == pid:
                        ext = f.name.rsplit(".", 1)[-1] if "." in f.name else "jpg"
                        save_name = f"{pid.lower()}.{ext}"
                        save_path = os.path.join(APP_DIR, "data", "images", save_name)
                        with open(save_path, "wb") as wf:
                            wf.write(f.getbuffer())
                        dm2.update_product(p["id"], {"image_file": save_name})
                        imported += 1
                        break
            st.success(f"已导入 {imported} 个商品图片！")
            st.rerun()

    st.divider()

    # 收款二维码上传（微信 + 支付宝）
    with st.expander("💳 收款二维码设置", expanded=False):
        st.markdown("上传微信和支付宝的收款码，顾客付款时可选择扫码方式")
        qr_wechat = os.path.join(APP_DIR, "data", "payment_qr_wechat.png")
        qr_alipay = os.path.join(APP_DIR, "data", "payment_qr_alipay.png")

        col_qr1, col_qr2 = st.columns(2)
        with col_qr1:
            st.markdown("**💚 微信收款码**")
            if os.path.exists(qr_wechat):
                st.image(qr_wechat, caption="当前微信收款码", use_container_width=True)
            wx_upload = st.file_uploader("上传微信收款码", type=["png", "jpg", "jpeg"], key="qr_wx_upload")
            if wx_upload is not None:
                with open(qr_wechat, "wb") as f:
                    f.write(wx_upload.getbuffer())
                st.success("微信收款码已更新！")
                st.rerun()

        with col_qr2:
            st.markdown("**💙 支付宝收款码**")
            if os.path.exists(qr_alipay):
                st.image(qr_alipay, caption="当前支付宝收款码", use_container_width=True)
            ali_upload = st.file_uploader("上传支付宝收款码", type=["png", "jpg", "jpeg"], key="qr_ali_upload")
            if ali_upload is not None:
                with open(qr_alipay, "wb") as f:
                    f.write(ali_upload.getbuffer())
                st.success("支付宝收款码已更新！")
                st.rerun()

    st.divider()

    # 操作模式
    mode = st.radio("操作", ["📋 商品列表", "➕ 添加商品", "✏️ 编辑商品"], horizontal=True)

    if mode == "📋 商品列表":
        products = dm.load_products()
        if not products:
            st.info("暂无商品")
            return

        df = pd.DataFrame(products)
        display_cols = {
            "id": "ID", "name": "名称", "category": "品类", "price": "单价",
            "unit": "单位", "stock": "库存", "is_active": "上架", "updated_at": "更新时间"
        }
        df_display = df[[c for c in display_cols if c in df.columns]].rename(columns=display_cols)

        # 库存预警
        def highlight_stock(val):
            try:
                if int(val) <= 5:
                    return "background-color: #ffe0e0; font-weight: bold; color: #c0392b"
            except Exception:
                pass
            return ""

        styled = df_display.style.map(highlight_stock, subset=["库存"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # 快速下架
        st.divider()
        st.markdown("**快速操作：下架商品**")
        active_products = [p for p in products if p.get("is_active")]
        if active_products:
            pid_to_delete = st.selectbox("选择要下架的商品", [p["id"] + " - " + p["name"] for p in active_products])
            if st.button("🔽 下架此商品", type="secondary"):
                actual_id = pid_to_delete.split(" - ")[0]
                if dm.delete_product(actual_id, hard=False):
                    st.success("已下架")
                    st.rerun()
        else:
            st.info("没有可下架的商品")

    elif mode == "➕ 添加商品":
        with st.form("add_product_form"):
            st.markdown("**新增商品**")
            name = st.text_input("商品名称 *")
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("品类 *", dm.categories)
                price = st.number_input("单价 (元) *", min_value=0.01, max_value=9999.0, step=0.01, format="%.2f")
            with col2:
                unit = st.text_input("单位 *", value="件", placeholder="瓶/袋/包/盒...")
                stock = st.number_input("库存数量 *", min_value=0, max_value=9999, step=1, value=10)
            emoji_raw = st.selectbox("商品图标（无图片时显示）", PRODUCT_EMOJIS, index=len(PRODUCT_EMOJIS)-1)
            emoji = emoji_raw.split()[0]

            col_img1, col_img2 = st.columns(2)
            with col_img1:
                uploaded_img = st.file_uploader("上传商品图片（推荐）", type=["png", "jpg", "jpeg", "webp"], key="add_img")
            with col_img2:
                image_url = st.text_input("或填图片链接", placeholder="https://...")

            desc = st.text_area("描述", placeholder="简短描述...")
            submitted = st.form_submit_button("✅ 添加商品", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("请输入商品名称")
                else:
                    image_file = ""
                    if uploaded_img is not None:
                        import uuid
                        ext = uploaded_img.name.split(".")[-1] if "." in uploaded_img.name else "jpg"
                        image_file = f"{uuid.uuid4().hex[:8]}.{ext}"
                        img_path = os.path.join(APP_DIR, "data", "images", image_file)
                        with open(img_path, "wb") as f:
                            f.write(uploaded_img.getbuffer())

                    pid = dm.add_product({
                        "name": name.strip(),
                        "category": category,
                        "price": round(price, 2),
                        "unit": unit.strip() or "件",
                        "stock": int(stock),
                        "image_emoji": emoji.strip() or "📦",
                        "image_file": image_file,
                        "image_url": (image_url or "").strip(),
                        "description": desc.strip() or "",
                    })
                    st.success(f"商品已添加，ID: {pid}")

    elif mode == "✏️ 编辑商品":
        products = dm.load_products()
        if not products:
            st.info("暂无商品可编辑")
            return

        product_opts = {f"{p['id']} - {p['name']}": p for p in products}
        selected = st.selectbox("选择要编辑的商品", list(product_opts.keys()))
        product = product_opts[selected]

        with st.form("edit_product_form"):
            st.markdown(f"**编辑商品：{product['name']}**")
            name = st.text_input("商品名称 *", value=product["name"])
            col1, col2, col3 = st.columns(3)
            with col1:
                cat_index = dm.categories.index(product["category"]) if product["category"] in dm.categories else 0
                category = st.selectbox("品类 *", dm.categories, index=cat_index)
            with col2:
                price = st.number_input("单价 (元) *", min_value=0.01, max_value=9999.0, value=float(product["price"]), step=0.01, format="%.2f")
            with col3:
                unit = st.text_input("单位 *", value=product.get("unit", "件"))
            col_a, col_b = st.columns(2)
            with col_a:
                stock = st.number_input("库存数量 *", min_value=0, max_value=9999, step=1, value=int(product.get("stock", 0)))
            with col_b:
                is_active = st.checkbox("上架", value=product.get("is_active", True))
            current_emoji = product.get("image_emoji", "📦")
            emoji_index = 0
            for i, e in enumerate(PRODUCT_EMOJIS):
                if e.startswith(current_emoji):
                    emoji_index = i
                    break
            emoji_raw = st.selectbox("商品图标", PRODUCT_EMOJIS, index=emoji_index)
            emoji = emoji_raw.split()[0]

            # 显示当前图片
            current_img = product.get("image_file", "")
            if current_img:
                img_path = os.path.join(APP_DIR, "data", "images", current_img)
                if os.path.exists(img_path):
                    st.image(img_path, width=120, caption="当前图片")
            col_eimg1, col_eimg2 = st.columns(2)
            with col_eimg1:
                uploaded_img = st.file_uploader("更换图片", type=["png", "jpg", "jpeg", "webp"], key="edit_img")
            with col_eimg2:
                image_url = st.text_input("或填图片链接", value=product.get("image_url", ""), placeholder="https://...")

            desc = st.text_area("描述", value=product.get("description", ""))

            submitted = st.form_submit_button("💾 保存修改", type="primary", use_container_width=True)
            if submitted:
                update_data = {
                    "name": name.strip(),
                    "category": category,
                    "price": round(price, 2),
                    "unit": unit.strip() or "件",
                    "stock": int(stock),
                    "is_active": is_active,
                    "image_emoji": emoji.strip() or "📦",
                    "image_url": (image_url or "").strip(),
                    "description": desc.strip() or "",
                }
                if uploaded_img is not None:
                    import uuid
                    ext = uploaded_img.name.split(".")[-1] if "." in uploaded_img.name else "jpg"
                    image_file = f"{uuid.uuid4().hex[:8]}.{ext}"
                    img_path = os.path.join(APP_DIR, "data", "images", image_file)
                    with open(img_path, "wb") as f:
                        f.write(uploaded_img.getbuffer())
                    update_data["image_file"] = image_file
                dm.update_product(product["id"], update_data)
                st.success("修改已保存")


# ============================================================
# 后台管理 — 订单管理
# ============================================================

def render_admin_orders():
    """订单管理页"""
    st.markdown("#### 📋 订单管理")

    orders = dm.load_orders()

    # 新订单提示音：检测是否有新增的待确认订单
    pending_count = sum(1 for o in orders if o.get("status") in ("待确认", "待核实"))
    last_seen = st.session_state.get("_last_seen_order_count", 0)
    if pending_count > 0 and pending_count > last_seen:
        # 播放提示音（自动播放在用户已交互过的页面上通常被允许）
        st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{BEEP_BASE64}" type="audio/wav">
        </audio>
        """, unsafe_allow_html=True)
        st.toast(f"🔔 您有 {pending_count} 笔待确认订单！", icon="🔔")
    # 更新"已读"计数
    st.session_state._last_seen_order_count = pending_count

    # 状态筛选
    statuses = ["全部", "待确认", "待核实", "已确认", "配送中", "已送达", "已取消"]
    status_filter = st.radio("按状态筛选", statuses, horizontal=True)

    filtered = orders
    if status_filter != "全部":
        filtered = [o for o in orders if o.get("status") == status_filter]

    if not filtered:
        st.info(f"暂无「{status_filter}」状态的订单")
        return

    st.markdown(f"共 **{len(filtered)}** 笔订单（总计 {len(orders)} 笔）")
    st.divider()

    for order in reversed(filtered):
        render_admin_order_card(order)


def render_admin_order_card(order: dict):
    """管理员订单卡片（含操作按钮）"""
    status = order.get("status", "未知")
    order_id = order.get("order_id", "")
    total = order.get("total_amount", 0)
    created = order.get("created_at", "")[:16].replace("T", " ")
    customer = order.get("customer_name", "")
    phone = order.get("customer_phone", "")
    address = order.get("delivery_address", "")
    items = order.get("items", [])
    note = order.get("note", "")
    history = order.get("status_history", [])

    with st.container():
        st.markdown(f"""
        <div class="order-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                <div>
                    <strong>{order_id}</strong>
                    <span style="color:#95a5a6;font-size:0.8rem;margin-left:0.8rem;">{created}</span>
                </div>
                <span class="status-badge status-{status}">{status}</span>
            </div>
            <div style="margin-top:0.3rem;font-size:0.9rem;color:#555;">
                👤 {customer} &nbsp; 📞 {phone} &nbsp; 📍 {address}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 付款核实提醒（待核实订单需要店主审核）
        if status == "待核实":
            st.warning("📱 **请核对手机上的微信/支付宝到账记录！** 确认金额无误后点击「核实通过」，金额不符点击「退回」")

        # 商品明细
        for item in items:
            emoji = item.get("emoji", "📦")
            st.markdown(f"  {emoji} {item.get('name','')} x{item.get('quantity',0)} - {format_price(item.get('subtotal',0))}")
        st.markdown(f"**订单金额: {format_price(total)}**")
        # 付款备注
        if note and "金额不符" in note:
            st.error(f"**付款异常!** {note}")
        elif note and "顾客声称已付" in note:
            st.info(f"{note}")
        elif note:
            st.markdown(f"备注: {note}")

        # 商品明细
        for item in items:
            emoji = item.get("emoji", "📦")
            st.markdown(f"  {emoji} {item.get('name','')} ×{item.get('quantity',0)} — {format_price(item.get('subtotal',0))}")
        st.markdown(f"**💰 订单金额：{format_price(total)}**")
        # 检查付款金额是否异常
        if note and "金额不符" in note:
            st.error(f"⚠️ **付款异常！** {note}")
        elif note and "顾客声称已付" in note:
            st.info(f"💬 {note}")
        elif note:
            st.markdown(f"💬 备注：{note}")

        # 状态操作按钮
        VALID_TRANSITIONS = {
            "待确认": ["待核实", "已确认", "已取消"],
            "待核实": ["已确认", "待确认", "已取消"],
            "已确认": ["配送中", "已取消"],
            "配送中": ["已送达"],
        }
        allowed = VALID_TRANSITIONS.get(status, [])
        if allowed:
            btn_cols = st.columns(len(allowed))
            for i, new_status in enumerate(allowed):
                with btn_cols[i]:
                    btn_label = {
                        "待核实": "🔍 标为待核实",
                        "已确认": "✅ 核实通过",
                        "待确认": "↩️ 退回重审",
                        "配送中": "🚀 开始配送",
                        "已送达": "📦 确认送达",
                        "已取消": "❌ 取消",
                    }.get(new_status, new_status)
                    # 待核实→核实通过 用蓝色主按钮突出
                    is_main = (status == "待核实" and new_status == "已确认")
                    if st.button(btn_label, key=f"adm_{order_id}_{new_status}",
                                 use_container_width=True,
                                 type="primary" if is_main else "secondary"):
                        ok, err = dm.update_order_status(order_id, new_status)
                        if ok:
                            st.success(f"订单 {order_id} → {new_status}")
                            st.rerun()
                        else:
                            st.error(err)

        # 订单轨迹
        if history:
            with st.expander("📋 订单轨迹"):
                for h in history:
                    ts = h.get("timestamp", "")[:16].replace("T", " ")
                    s = h.get("status", "")
                    st.markdown(f"- {ts} → <span class='status-badge status-{s}'>{s}</span>", unsafe_allow_html=True)

        st.divider()


# ============================================================
# 后台管理 — 数据统计
# ============================================================


def render_admin_announcements():
    """公告管理"""
    st.markdown("#### 📢 公告管理")
    with st.form("announce_form", clear_on_submit=True):
        st.markdown("**发布新公告**")
        a_title = st.text_input("公告标题")
        col_a1, col_a2 = st.columns([2, 1])
        with col_a1:
            a_content = st.text_area("公告内容")
        with col_a2:
            a_type = st.selectbox("公告类型", ["通知", "促销", "紧急"])
        if st.form_submit_button("📢 发布公告", type="primary", use_container_width=True):
            if a_title.strip() and a_content.strip():
                dm.add_announcement(a_title.strip(), a_content.strip(), a_type)
                st.success("公告已发布！")
                st.rerun()
            else:
                st.error("请填写标题和内容")

    st.divider()
    anns = dm.load_announcements()
    if not anns:
        st.info("暂无公告")
    else:
        for ann in reversed(anns):
            active = ann.get("is_active", True)
            icon_map = {"促销": "🎉", "紧急": "🔴", "通知": "📢"}
            icon = icon_map.get(ann.get("type", ""), "📢")
            status_text = "✅ 显示中" if active else "⏸️ 已隐藏"
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.markdown(f"{icon} **{ann['title']}** — {ann['content']}")
                    st.caption(f"{ann.get('type','')} | {ann.get('created_at','')[:10]} | {status_text}")
                with col2:
                    toggle_label = "⏸️ 隐藏" if active else "✅ 显示"
                    if st.button(toggle_label, key=f"toggle_{ann['id']}", use_container_width=True):
                        dm.toggle_announcement(ann["id"])
                        st.rerun()
                with col3:
                    if st.button("🗑️ 删除", key=f"delann_{ann['id']}", use_container_width=True):
                        dm.delete_announcement(ann["id"])
                        st.rerun()
                st.divider()

def render_admin_analytics():
    """数据统计页"""
    st.markdown("#### 📊 数据统计")

    stats = dm.get_stats()

    # KPI 行
    kpi_items = [
        ("📋", "总订单数", stats["total_orders"]),
        ("💰", "总营收", f"¥{stats['total_revenue']:,.2f}"),
        ("⏳", "待处理", stats["pending_orders"]),
        ("📅", "今日订单", stats["today_orders"]),
    ]

    kpi_cols = st.columns(4)
    for i, (icon, label, value) in enumerate(kpi_items):
        with kpi_cols[i]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 图表行
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("##### 🥧 品类销售占比")
        category_sales = stats.get("category_sales", {})
        if category_sales:
            fig_pie = px.pie(
                names=list(category_sales.keys()),
                values=list(category_sales.values()),
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_pie.update_traces(textinfo="label+percent", hole=0.35)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350,
                                  template="plotly_white")
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("暂无销售数据")

    with chart_col2:
        st.markdown("##### 📈 近7天订单趋势")
        daily = stats.get("daily_orders", {})
        if daily:
            df_daily = pd.DataFrame(list(daily.items()), columns=["日期", "订单数"])
            fig_bar = px.bar(
                df_daily, x="日期", y="订单数",
                color_discrete_sequence=["#3498db"],
                text="订单数",
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350,
                                  template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("暂无订单数据")

    # 热销排行
    st.divider()
    st.markdown("##### 🏆 热销商品排行")
    top = dm.get_top_products(10)
    if top:
        df_top = pd.DataFrame(top)
        df_top.index = range(1, len(df_top) + 1)
        df_top["revenue"] = df_top["revenue"].apply(lambda x: f"¥{x:.2f}")
        df_top_display = df_top.rename(columns={"name": "商品", "quantity": "销量", "revenue": "销售额"})
        st.dataframe(
            df_top_display[["商品", "销量", "销售额"]],
            use_container_width=True,
            hide_index=False,
        )
    else:
        st.info("暂无销售数据")


# ============================================================
# 主入口
# ============================================================

def render_staff_panel():
    """店员面板：只能看订单+统计"""
    if not st.session_state.staff_authenticated:
        st.markdown("### 👷 店员登录")
        with st.form("staff_login_form"):
            pwd = st.text_input("请输入店员密码", type="password")
            if st.form_submit_button("登录", type="primary", use_container_width=True):
                if pwd == dm.staff_password:
                    st.session_state.staff_authenticated = True
                    st.success("✅ 登录成功！")
                    st.rerun()
                else:
                    st.error("❌ 密码错误")
        return

    st.markdown("### 👷 店员面板")
    staff_tabs = st.tabs(["📋 订单管理", "📊 数据统计"])
    with staff_tabs[0]:
        render_admin_orders()
    with staff_tabs[1]:
        render_admin_analytics()


def main():
    render_sidebar()

    if st.session_state.role == "customer":
        render_customer()
    elif st.session_state.role == "staff":
        render_staff_panel()
    else:
        render_admin_panel()


if __name__ == "__main__":
    main()
