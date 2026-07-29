"""
便利店在线商城 - 初始商品数据
运行此脚本将写入 data/products.json
"""

from data_manager import DataManager


def seed_products():
    """写入初始商品数据（约 25 个商品，覆盖 6 大品类）"""
    dm = DataManager()
    dm.reinitialize_data()

    products = [
        # ===== 零食 (5) =====
        {
            "name": "乐事原味薯片",
            "category": "零食",
            "price": 8.50,
            "unit": "袋",
            "stock": 30,
            "image_emoji": "🍟",
            "description": "70g袋装，经典原味",
        },
        {
            "name": "奥利奥夹心饼干",
            "category": "零食",
            "price": 9.90,
            "unit": "盒",
            "stock": 25,
            "image_emoji": "🍪",
            "description": "巧克力味 97g盒装",
        },
        {
            "name": "良品铺子猪肉脯",
            "category": "零食",
            "price": 15.00,
            "unit": "袋",
            "stock": 20,
            "image_emoji": "🥩",
            "description": "蜜汁味猪肉脯 100g",
        },
        {
            "name": "卫龙辣条",
            "category": "零食",
            "price": 3.50,
            "unit": "袋",
            "stock": 50,
            "image_emoji": "🌶️",
            "description": "经典大面筋 106g",
        },
        {
            "name": "三只松鼠坚果礼盒",
            "category": "零食",
            "price": 49.90,
            "unit": "盒",
            "stock": 10,
            "image_emoji": "🥜",
            "description": "每日坚果混合装 750g",
        },

        # ===== 饮料 (5) =====
        {
            "name": "红牛维生素饮料",
            "category": "饮料",
            "price": 6.00,
            "unit": "罐",
            "stock": 40,
            "image_emoji": "🥤",
            "description": "250ml罐装，提神抗疲劳",
        },
        {
            "name": "可口可乐",
            "category": "饮料",
            "price": 3.50,
            "unit": "瓶",
            "stock": 60,
            "image_emoji": "🥃",
            "description": "500ml瓶装，冰镇更好喝",
        },
        {
            "name": "农夫山泉",
            "category": "饮料",
            "price": 2.00,
            "unit": "瓶",
            "stock": 80,
            "image_emoji": "💧",
            "description": "550ml瓶装，天然矿泉水",
        },
        {
            "name": "元气森林气泡水",
            "category": "饮料",
            "price": 5.50,
            "unit": "瓶",
            "stock": 35,
            "image_emoji": "🫧",
            "description": "白桃味 480ml，0糖0卡",
        },
        {
            "name": "王老吉凉茶",
            "category": "饮料",
            "price": 5.00,
            "unit": "罐",
            "stock": 30,
            "image_emoji": "🍵",
            "description": "310ml罐装，怕上火喝王老吉",
        },

        # ===== 烟 (4) =====
        {
            "name": "中华（软）",
            "category": "烟",
            "price": 70.00,
            "unit": "包",
            "stock": 15,
            "image_emoji": "🚬",
            "description": "软包中华，经典国烟",
        },
        {
            "name": "芙蓉王（硬蓝）",
            "category": "烟",
            "price": 35.00,
            "unit": "包",
            "stock": 20,
            "image_emoji": "🚬",
            "description": "硬蓝芙蓉王，湖南名烟",
        },
        {
            "name": "黄鹤楼（软蓝）",
            "category": "烟",
            "price": 19.00,
            "unit": "包",
            "stock": 25,
            "image_emoji": "🚬",
            "description": "软蓝黄鹤楼，湖北名烟",
        },
        {
            "name": "利群（新版）",
            "category": "烟",
            "price": 16.00,
            "unit": "包",
            "stock": 30,
            "image_emoji": "🚬",
            "description": "新版利群，浙江名烟",
        },

        # ===== 酒 (4) =====
        {
            "name": "雪花啤酒",
            "category": "酒",
            "price": 4.00,
            "unit": "罐",
            "stock": 60,
            "image_emoji": "🍺",
            "description": "勇闯天涯 500ml罐装",
        },
        {
            "name": "茅台迎宾酒",
            "category": "酒",
            "price": 168.00,
            "unit": "瓶",
            "stock": 8,
            "image_emoji": "🍶",
            "description": "53度酱香型白酒 500ml",
        },
        {
            "name": "张裕解百纳干红",
            "category": "酒",
            "price": 89.00,
            "unit": "瓶",
            "stock": 12,
            "image_emoji": "🍷",
            "description": "特选级干红葡萄酒 750ml",
        },
        {
            "name": "RIO锐澳鸡尾酒",
            "category": "酒",
            "price": 12.00,
            "unit": "瓶",
            "stock": 25,
            "image_emoji": "🍹",
            "description": "蓝玫瑰味 275ml",
        },

        # ===== 槟榔 (4) =====
        {
            "name": "口味王槟榔",
            "category": "槟榔",
            "price": 15.00,
            "unit": "袋",
            "stock": 40,
            "image_emoji": "🫘",
            "description": "经典咖啡味 28g",
        },
        {
            "name": "伍子醉槟榔",
            "category": "槟榔",
            "price": 10.00,
            "unit": "袋",
            "stock": 35,
            "image_emoji": "🫘",
            "description": "枸杞槟榔 20g",
        },
        {
            "name": "胖哥槟榔",
            "category": "槟榔",
            "price": 12.00,
            "unit": "袋",
            "stock": 30,
            "image_emoji": "🫘",
            "description": "青果槟榔 25g",
        },
        {
            "name": "皇爷槟榔",
            "category": "槟榔",
            "price": 8.00,
            "unit": "袋",
            "stock": 25,
            "image_emoji": "🫘",
            "description": "经典芝麻味 18g",
        },

        # ===== 日用品 (4) =====
        {
            "name": "维达抽纸",
            "category": "日用品",
            "price": 15.90,
            "unit": "提",
            "stock": 20,
            "image_emoji": "🧻",
            "description": "超韧系列 3层×120抽×6包",
        },
        {
            "name": "蓝月亮洗衣液",
            "category": "日用品",
            "price": 29.90,
            "unit": "瓶",
            "stock": 15,
            "image_emoji": "🧴",
            "description": "深层洁净 1kg瓶装",
        },
        {
            "name": "舒肤佳洗手液",
            "category": "日用品",
            "price": 12.90,
            "unit": "瓶",
            "stock": 18,
            "image_emoji": "🧼",
            "description": "抑菌泡沫洗手液 225ml",
        },
        {
            "name": "高露洁牙膏",
            "category": "日用品",
            "price": 13.90,
            "unit": "支",
            "stock": 25,
            "image_emoji": "🪥",
            "description": "360°卓效护龈 140g",
        },
    ]

    for p in products:
        dm.add_product(p)

    print(f"[OK] Written {len(products)} products to {dm.products_path}")
    return len(products)


if __name__ == "__main__":
    seed_products()
