import requests
import gzip
import json
import re
import xml.etree.ElementTree as ET
from io import BytesIO

# ======================
# 配置
# ======================
EPG_URL = "https://github.com/badboys88888/epg/raw/refs/heads/main/epg.xml.gz"
ICON_MAP_URL = "https://raw.githubusercontent.com/badboys88888/epg/refs/heads/main/icon_map.json"

OUTPUT_FILE = "epg.xml.gz"

# ======================
# icon_map
# ======================
icon_map = requests.get(ICON_MAP_URL).json()

def normalize(text: str) -> str:
    text = text.upper()
    text = re.sub(r"[ \-_]", "", text)
    return text

norm_icon_map = {normalize(k): v for k, v in icon_map.items()}

# ======================
# 下载EPG
# ======================
resp = requests.get(EPG_URL)
xml_data = gzip.decompress(resp.content)

root = ET.fromstring(xml_data)

# ======================
# 处理 channel
# ======================
for ch in root.findall("channel"):

    names = [d.text for d in ch.findall("display-name") if d.text]

    # -------- logo --------
    icon_url = None
    for n in names:
        key = normalize(n)
        if key in norm_icon_map:
            icon_url = norm_icon_map[key]
            break

    if icon_url:
        icon = ch.find("icon")
        if icon is None:
            icon = ET.SubElement(ch, "icon")
        icon.set("src", icon_url)

    # -------- CID --------
    main_name = names[0] if names else "UNKNOWN"
    cid = normalize(main_name)

    ch.set("id", cid)

# ======================
# 写入 gz（关键补全）
# ======================
new_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

with gzip.open(OUTPUT_FILE, "wb") as f:
    f.write(new_xml)

print("完成生成:", OUTPUT_FILE)
