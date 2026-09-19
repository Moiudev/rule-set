#!/usr/bin/env python3
# /scripts/parse/parse_domain.py

"""
中国加速域名解析，专门处理 [domain] 分组下的规则源。
"""

from pathlib import Path

from scripts.config import CLEAN_ROOT
from scripts.parse.common import parse_group, save_sorted_rules, is_valid_domain


def extract_domain(line: str) -> str:
    if line.startswith(("server=", "address=")):
        parts = line.split("/")
        if len(parts) >= 2:
            return parts[1].strip()
    if "," in line:
        for part in line.split(","):
            part = part.strip()
            upper = part.upper()
            if upper.startswith(("DOMAIN", "IP", "PROCESS")):
                continue
            if "." in part:
                return part.lstrip(".")
    if "." in line and not line.startswith(("#", "!", "[", "http", "server=", "address=")):
        return line.split()[0].lstrip(".")
    return ""


def parse_domain_group(raw_dir: Path):
    all_rules = parse_group(raw_dir=raw_dir, extractor=extract_domain, validator=is_valid_domain)
    sorted_rules = sorted(all_rules, key=str.lower)
    save_sorted_rules(CLEAN_ROOT / f"{raw_dir.name}.txt", sorted_rules)