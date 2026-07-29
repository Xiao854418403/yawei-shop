"""
批量导入商品图片
把图片放到 data/images/ 文件夹，文件名匹配商品 ID 即可
例如：P001.jpg 会自动匹配到 ID 为 P001 的商品
"""
import os, json, shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

os.makedirs(IMAGES_DIR, exist_ok=True)

with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

products = data["products"]
matched = 0

for filename in os.listdir(IMAGES_DIR):
    name_no_ext = os.path.splitext(filename)[0].upper()  # P001
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        continue

    for p in products:
        if p["id"].upper() == name_no_ext:
            p["image_file"] = filename
            print(f"  {p['id']} -> {filename} ✓")
            matched += 1
            break
    else:
        print(f"  {filename} -> 未找到匹配商品，跳过")

with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n完成！{matched} 个商品已匹配图片")
input("\n按回车退出...")
