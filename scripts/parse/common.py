#!/usr/bin/env python3
# /scripts/parse/common.py

"""
通用解析工具，提供行清理、通用分组解析、排序保存等函数。
"""

from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import idna

from scripts.utils.file_io import write_lines
from scripts.utils.logger import init_logger

logger = init_logger(__name__)


def clean_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if line.startswith(("#", "!")):
        return ""
    if "#" in line:
        line = line.split("#", 1)[0].strip()
    return line


def normalize_domain(domain: str) -> str:
    if not domain:
        return ""
    domain = domain.strip()
    if "://" in domain:
        try:
            parsed = urlparse(domain)
            domain = parsed.hostname or ""
        except Exception:
            return ""
    if ":" in domain:
        domain = domain.split(":", 1)[0]
    if domain.startswith("*."):
        domain = domain[2:]
    domain = (domain.strip().rstrip(".").strip(" ,;|").casefold())
    if not domain:
        return ""
    try:
        domain = idna.encode(domain, uts46=True).decode("ascii")
    except Exception:
        return ""
    return domain


def is_valid_domain(domain: str) -> bool:
    if not domain:
        return False
    if len(domain) > 255:
        return False
    if "." not in domain:
        return False
    if domain.startswith((".", "-")):
        return False
    if domain.endswith((".", "-")):
        return False
    try:
        ascii_domain = idna.encode(domain, uts46=True).decode("ascii")
    except Exception:
        return False
    if not all(c.isalnum() or c in ".-" for c in ascii_domain):
        return False
    labels = ascii_domain.split(".")
    for label in labels:
        if not label:
            return False
        if len(label) > 63:
            return False
        if label.startswith("-"):
            return False
        if label.endswith("-"):
            return False
    if len(labels[-1]) < 2:
        return False
    return True


def parse_group(
        raw_dir: Path,
        extractor: Callable[[str], str],
        validator: Callable[[str], bool],
        normalizer: Callable[[str], str] | None = None,
) -> set[str]:
    all_rules: set[str] = set()
    logger.info(f"开始处理 [{raw_dir.name}] 分组...")
    for raw_file in raw_dir.glob("*.txt"):
        raw_count = 0
        valid_count = 0
        try:
            with raw_file.open(mode="r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    raw_count += 1
                    cleaned = clean_line(line)
                    if not cleaned:
                        continue
                    value = extractor(cleaned)
                    if not value:
                        continue
                    if normalizer:
                        value = normalizer(value)
                    if validator(value):
                        all_rules.add(value)
                        valid_count += 1
            logger.info(f"{raw_file.name} 解析完成，原始 {raw_count} 行，有效 {valid_count} 条。")
        except Exception as e:
            logger.error(f"{raw_file.name} 解析失败: {e}")
    return all_rules


def save_sorted_rules(output_path: Path, rules: list[str]):
    write_lines(output_path, rules)
    logger.info(f"{output_path.name} 写入完成，共 {len(rules)} 条规则。")