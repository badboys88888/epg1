#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import xml.etree.ElementTree as ET
import re
from opencc import OpenCC

INPUT = "epg.xml.gz"
OUTPUT = "name_map.txt"

# 初始化繁体 → 简体
cc = OpenCC('t2s')


# ======================
# normalize（核心）
# ======================
def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.upper()                # 小写 → 大写
    text = re.sub(r"[ \-_]", "", text)  # 去空格、-、_
    return text


# ======================
# 读取EPG
# ======================
def load_epg_names():
    names = set()

    with gzip.open(INPUT, "rb") as f:
        root = ET.parse(f).getroot()

    for ch in root.findall("channel"):
        for d in ch.findall("display-name"):
            if d.text:
                names.add(d.text.strip())

    return names


# ======================
# 生成映射
# ======================
def build_map(names):
    result = []

    for name in sorted(names):
        key = normalize(name)
        simple = cc.convert(name)  # 保持原格式，仅繁→简

        result.append(f"{key}={simple}")

    return result


# ======================
# 写入文件
# ======================
def save_map(lines):
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ======================
# 主程序
# ======================
def main():
    names = load_epg_names()
    print(f"[INFO] 读取频道数: {len(names)}")

    lines = build_map(names)
    save_map(lines)

    print(f"[OK] 生成 name_map.txt: {len(lines)} 条")


if __name__ == "__main__":
    main()
