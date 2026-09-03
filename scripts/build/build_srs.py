#!/usr/bin/env python3
# /scripts/build/build_srs.py

"""
构建 .srs 规则集。
"""

import shutil
import subprocess

from scripts.config import PROJECT_ROOT, DOMAIN_RULESETS, IP_RULESETS
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

RULESETS: tuple[str, ...] = tuple(DOMAIN_RULESETS) + tuple(IP_RULESETS)
TIMEOUT = 30


def check_sing_box() -> bool:
    if shutil.which("sing-box"):
        return True
    logger.warning("未找到 sing-box 命令，跳过 .srs 转换！")
    return False


def convert_to_srs(name: str):
    json_path = PROJECT_ROOT / f"{name}.json"
    if not json_path.exists():
        logger.warning(f"{json_path.name} 不存在，跳过。")
        return
    srs_path = PROJECT_ROOT / f"{name}.srs"
    try:
        result = subprocess.run(
            ["sing-box", "rule-set", "compile", "--output", str(srs_path), str(json_path)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        if result.returncode == 0:
            logger.info(f"{srs_path.name} 已生成！")
        else:
            logger.warning(f"{srs_path.name} 转换失败：{result.stderr.strip()}")
    except Exception as e:
        logger.error(f"{name}.srs 转换异常：{e}")


def build_all_srs():
    logger.info("开始生成 .srs 规则集...")
    if not check_sing_box():
        return
    for name in RULESETS:
        convert_to_srs(name)
    logger.info("所有 .srs 规则集已生成！")