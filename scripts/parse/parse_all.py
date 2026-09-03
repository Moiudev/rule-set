#!/usr/bin/env python3
# /scripts/parse/parse_all.py

"""
通用解析入口，读取 sources.toml 配置文件，根据每个分组（ads/domain/ip）调用对应的解析器，完成所有原始规则文件的解析。
"""

import tomllib

from scripts.config import RAW_ROOT, SOURCES_PATH
from scripts.parse.parse_ads import parse_ads_group
from scripts.parse.parse_domain import parse_domain_group
from scripts.parse.parse_ip import parse_ip_group
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

PARSERS = {
    "ads": parse_ads_group,
    "domain": parse_domain_group,
    "ip": parse_ip_group,
}


def load_sources() -> dict:
    if not SOURCES_PATH.exists():
        logger.error(f"{SOURCES_PATH} 配置文件不存在！")
        return {}
    try:
        with SOURCES_PATH.open("rb") as f:
            return tomllib.load(f)
    except Exception as e:
        logger.error(f"读取 sources.toml 失败: {e}")
        return {}


def parse_all():
    sources = load_sources()
    if not sources:
        return
    logger.info("开始解析所有规则...")
    for group in sources.keys():
        parser = PARSERS.get(group)
        if not parser:
            logger.warning(f"{group} 未找到解析器，跳过。")
            continue
        try:
            parser(RAW_ROOT / group)
        except Exception as e:
            logger.error(f"{group} 分组解析失败: {e}")
    logger.info("所有规则解析完成！")