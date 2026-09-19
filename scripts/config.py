#!/usr/bin/env python3
# /scripts/config.py

"""
定义脚本中使用到的全局路径和生成的规则集。
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_ROOT = PROJECT_ROOT / "rules"
RAW_ROOT = RULES_ROOT / "raw"
CLEAN_ROOT = RULES_ROOT / "clean"
CUSTOM_ROOT = RULES_ROOT / "custom"
SOURCES_PATH = RULES_ROOT / "sources.toml"

# 域名类规则集
DOMAIN_RULESETS: dict[str, list[str]] = {
    "ads": [
        "ads.txt",
        "custom/domain_ads.txt",
        "dlc/category-ads-all.txt"
    ],
    "geosite-cn": [
        "custom/domain_cn.txt",
        "domain.txt",
        "dlc/cn.txt"
    ],
    "geolocation-cn": [
        "dlc/geolocation-cn.txt"
    ],
    "geolocation-!cn": [
        "dlc/geolocation-!cn.txt"
    ],
    "porn": [
        "dlc/category-porn.txt"
    ],
    "httpdns-cn": [
        "dlc/category-httpdns-cn.txt"
    ]
}

# IP 类规则集
IP_RULESETS: dict[str, list[str]] = {
    "geoip-cn": ["ip.txt"],
}