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
# normalize
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
icon_map = requests.get(ICON_MAP_URL).json()
norm_icon_map = {normalize(k): v for k, v in icon_map.items()}


# ======================
# 读取 name_map
# ======================
groups = {}

with open(NAME_MAP_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "=" not in line:
            continue

        raw, std = line.split("=", 1)

        raw = raw.strip()
        std = std.strip()

        if std not in groups:
            groups[std] = []

        groups[std].append(raw)


# ======================
# 生成 epg.json
# ======================
epgs = []

for std_name, alias_list in groups.items():

    key = normalize(std_name)

    # 匹配logo
    logo = norm_icon_map.get(key, "")

    epgs.append({
        "epgid": std_name,
        "logo": logo,
        "name": ",".join(alias_list)
    })


# ======================
# 输出
# ======================
result = {
    "epgs": epgs
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✔ 生成 epg.json:", len(epgs))
