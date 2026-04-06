import json
import re
import requests

# ======================
# 配置
# ======================
NAME_MAP_FILE = "name_map1.txt"
ICON_MAP_URL = "https://raw.githubusercontent.com/badboys88888/epg/refs/heads/main/icon_map.json"

OUTPUT = "epg.json"


# ======================
# normalize（核心）
# ======================
def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.upper()
    text = re.sub(r"[ \-_]", "", text)
    return text


# ======================
# 读取 icon_map
# ======================
print("加载 icon_map...")
icon_map = requests.get(ICON_MAP_URL, timeout=30).json()

# 统一key
norm_icon_map = {normalize(k): v for k, v in icon_map.items()}


# ======================
# 读取 name_map
# ======================
print("读取 name_map...")

groups = {}

with open(NAME_MAP_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line or "=" not in line:
            continue

        raw, std = line.split("=", 1)

        raw = raw.strip()
        std = std.strip()

        if not raw or not std:
            continue

        if std not in groups:
            groups[std] = set()

        groups[std].add(raw)
        groups[std].add(std)   # 标准名也加进去


# ======================
# 生成 epg.json
# ======================
print("生成 epg.json...")

epgs = []
miss_logo = 0

for std_name, alias_set in groups.items():

    epgid = normalize(std_name)

    # ---------- logo ----------
    logo = norm_icon_map.get(epgid, "")

    if not logo:
        miss_logo += 1
        print("⚠ 未匹配logo:", std_name)

    # ---------- name ----------
    # 标准名放第一位
    names = [std_name] + [n for n in alias_set if n != std_name]

    epgs.append({
        "epgid": epgid,
        "logo": logo,
        "name": ",".join(names)
    })


# ======================
# 输出
# ======================
result = {
    "epgs": epgs
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n✔ 完成")
print("频道数:", len(epgs))
print("未匹配logo:", miss_logo)
