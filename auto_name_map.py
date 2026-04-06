import gzip
import xml.etree.ElementTree as ET
import re
from opencc import OpenCC

INPUT = "epg.xml.gz"
OUTPUT = "name_map.txt"

# 初始化繁→简
cc = OpenCC('t2s')


# ======================
# normalize（关键）
# ======================
def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.upper()
    text = re.sub(r"[ \-_]", "", text)
    return text


# ======================
# 读取EPG
# ======================
with gzip.open(INPUT, "rb") as f:
    root = ET.parse(f).getroot()

names = set()

for ch in root.findall("channel"):
    for d in ch.findall("display-name"):
        if d.text:
            names.add(d.text.strip())


# ======================
# 生成映射
# ======================
result = []

for name in sorted(names):

    key = normalize(name)

    # 👉 完整繁→简
    simple = cc.convert(name)

    result.append(f"{key}={simple}")


# ======================
# 写入
# ======================
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(result))

print("✔ 生成 name_map:", len(result))
