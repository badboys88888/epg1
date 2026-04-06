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

OUTPUT_FILE = "epg_new.xml.gz"

# ======================
# 读取 icon_map
# ======================
icon_map = requests.get(ICON_MAP_URL).json()

# ======================
# normalize（保留HD）
# ======================
def normalize(text: str) -> str:
    text = text.upper()
    text = re.sub(r"[ \-\_]", "", text)
    return text

norm_icon_map = {normalize(k): v for k, v in icon_map.items()}

# ======================
# 下载 EPG
# ======================
resp = requests.get(EPG_URL)
data = resp.content

# 解压 gz
xml_data = gzip.decompress(data)

# 解析 XML
root = ET.fromstring(xml_data)

# ======================
# 处理 channel
# ======================
for ch in root.findall("channel"):

    names = [d.text for d in ch.findall("display-name") if d.text]

    # -------- logo匹配 --------
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

    # -------- CID重建（保留HD）--------
    main_name = names[0] if names else "UNKNOWN"
    cid = normalize(main_name)

    ch.set("id", cid)

# ======================
# 写回 gz
# ======================
new_xml = ET.tostring(root, encoding="utf-8")

with gzip.open(OUTPUT_FILE, "wb") as f:
    f.write(new_xml)

print("完成：", OUTPUT_FILE)
