import requests
import gzip
import re
import xml.etree.ElementTree as ET

# ======================
# 配置
# ======================
EPG_URL = "https://github.com/badboys88888/epg/raw/refs/heads/main/epg.xml.gz"
ICON_MAP_URL = "https://raw.githubusercontent.com/badboys88888/epg/refs/heads/main/icon_map.json"

OUTPUT_FILE = "epg.xml.gz"


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
# icon_map
# ======================
icon_map = requests.get(ICON_MAP_URL).json()
norm_icon_map = {normalize(k): v for k, v in icon_map.items()}


# ======================
# 下载EPG
# ======================
resp = requests.get(EPG_URL)
xml_data = gzip.decompress(resp.content)

root = ET.fromstring(xml_data)


# ======================
# 核心：统一CID
# ======================
name_to_cid = {}   # 名字 → 统一CID
old_to_new = {}    # 旧CID → 新CID

for ch in root.findall("channel"):

    old_id = ch.get("id")
    names = [d.text for d in ch.findall("display-name") if d.text]

    if not names:
        continue

    main_name = names[0]
    key = normalize(main_name)

    # 第一次出现，注册统一CID
    if key not in name_to_cid:
        name_to_cid[key] = key

    new_id = name_to_cid[key]

    old_to_new[old_id] = new_id
    ch.set("id", new_id)

    # ======================
    # logo
    # ======================
    icon_url = None

    for n in names:
        k = normalize(n)
        if k in norm_icon_map:
            icon_url = norm_icon_map[k]
            break

    if icon_url:
        icon = ch.find("icon")
        if icon is None:
            icon = ET.SubElement(ch, "icon")

        icon.set("src", icon_url)


# ======================
# programme同步（关键）
# ======================
for p in root.findall("programme"):
    old = p.get("channel")

    if old in old_to_new:
        p.set("channel", old_to_new[old])


# ======================
# 去重 channel（关键）
# ======================
seen = set()

for ch in list(root.findall("channel")):
    cid = ch.get("id")

    if cid in seen:
        root.remove(ch)
    else:
        seen.add(cid)


# ======================
# 输出 gz
# ======================
xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)

with gzip.open(OUTPUT_FILE, "wb") as f:
    f.write(xml_bytes)

print("✔ 完成：统一CID + logo + 去重")
