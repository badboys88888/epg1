import requests
import gzip
import xml.etree.ElementTree as ET

# ======================
# 配置
# ======================
EPG_URL = "https://github.com/badboys88888/epg/raw/refs/heads/main/epg.xml.gz"
ICON_MAP_URL = "https://raw.githubusercontent.com/badboys88888/epg/refs/heads/main/icon_map.json"
ALIAS_URL = "https://raw.githubusercontent.com/badboys88888/epg/refs/heads/main/alias_auto.txt"

OUTPUT_FILE = "epg.xml.gz"


# ======================
# 统一规范函数
# ======================
def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.upper()
    text = text.replace(" ", "")
    text = text.replace("\t", "")
    text = text.replace("-", "")
    text = text.replace("_", "")
    return text


# ======================
# 读取 icon_map（远程）
# ======================
icon_map = requests.get(ICON_MAP_URL, timeout=30).json()
norm_icon_map = {normalize(k): v for k, v in icon_map.items()}


# ======================
# 读取 alias（远程）
# ======================
alias_map = {}

alias_text = requests.get(ALIAS_URL, timeout=30).text.splitlines()

for line in alias_text:
    line = line.strip()
    if not line or "=" not in line:
        continue

    cid, name = line.split("=", 1)
    cid = cid.strip()
    name = name.strip()

    # 用 display-name 做 key
    alias_map[normalize(name)] = cid


# ======================
# 下载 EPG
# ======================
resp = requests.get(EPG_URL, timeout=30)
xml_data = gzip.decompress(resp.content)

root = ET.fromstring(xml_data)


# ======================
# 处理 channel
# ======================
for ch in root.findall("channel"):

    names = [d.text for d in ch.findall("display-name") if d.text]
    if not names:
        continue

    # ======================
    # CID生成
    # ======================
    main_name = names[0]
    base_id = normalize(main_name)

    # alias修正
    cid = alias_map.get(base_id, base_id)

    ch.set("id", cid)

    # ======================
    # logo匹配
    # ======================
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


# ======================
# 输出 gzip
# ======================
xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)

with gzip.open(OUTPUT_FILE, "wb") as f:
    f.write(xml_bytes)

print("✔ 完成EPG重建:", OUTPUT_FILE)
