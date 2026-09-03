#!/usr/bin/env python3
# /scripts/parse/parse_ads.py

"""
广告域名规则解析，专门处理 [ads] 分组下的规则源，支持多种常见广告规则格式，如 ABP、AdGuard、hosts 等。
"""

from pathlib import Path

from scripts.config import CLEAN_ROOT
from scripts.parse.common import parse_group, save_sorted_rules, normalize_domain, is_valid_domain, clean_line
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

INVALID_PREFIXES = ("#", "!", "[", "<")
HOST_PREFIXES = ("127.0.0.1", "0.0.0.0")


def extract_domain(line: str) -> str:
    cleaned = clean_line(line)
    if cleaned.startswith("||"):
        return cleaned[2:].split("^")[0].split("/")[0].split("$")[0].split(",")[0]
    if cleaned.startswith("server=/"):
        parts = cleaned.split('/')
        if len(parts) >= 2:
            return parts[1].strip()
    if any(cleaned.startswith(prefix) for prefix in HOST_PREFIXES):
        parts = cleaned.split()
        if len(parts) >= 2:
            return parts[1]
    if "." in cleaned and not cleaned.startswith(INVALID_PREFIXES):
        domain = cleaned.split()[0].split("^")[0].split("$")[0].split(",")[0]
        return domain
    return ""


def parse_ads_group(raw_dir: Path):
    all_rules = parse_group(
        raw_dir=raw_dir,
        extractor=extract_domain,
        validator=is_valid_domain,
        normalizer=normalize_domain,
    )
    sorted_rules = sorted(all_rules)
    save_sorted_rules(CLEAN_ROOT / f"{raw_dir.name}.txt", sorted_rules)