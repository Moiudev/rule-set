#!/usr/bin/env python3
# /scripts/download/download_rules.py

"""
读取 sources.toml 并下载所有规则文件。
"""

import tomllib

from scripts.config import SOURCES_PATH, RAW_ROOT
from scripts.download.downloader import download
from scripts.utils.file_io import ensure_dir
from scripts.utils.logger import init_logger

logger = init_logger(__name__)


def load_sources() -> dict:
    if not SOURCES_PATH.exists():
        logger.error(f"{SOURCES_PATH} 配置文件不存在！")
        return {}
    try:
        with SOURCES_PATH.open("rb") as f:
            data = tomllib.load(f)
        logger.info(f"读取 {SOURCES_PATH} 成功，共 {len(data)} 个分组。")
        return data
    except Exception as e:
        logger.error(f"读取 sources.toml 失败，错误: {e}")
        return {}


def download_all_rules():
    sources = load_sources()
    if not sources:
        logger.warning("未找到规则源配置！")
        return
    logger.info("开始下载所有规则源...")
    total_groups = len(sources)
    for group_idx, (group_name, group_rules) in enumerate(sources.items(), 1):
        logger.info(f"[{group_idx}/{total_groups}] 正在处理 [{group_name}] 分组，共 {len(group_rules)} 个源。")
        group_dir = RAW_ROOT / group_name
        ensure_dir(group_dir)
        for rule_name, rule_url in group_rules.items():
            save_path = group_dir / f"{rule_name}.txt"
            logger.info(f"开始下载 {rule_name}...")
            success = download(rule_url, save_path)
            if not success:
                logger.warning(f"{rule_name} 下载失败！")
    logger.info("所有规则下载完成！")