#!/usr/bin/env python3
# /scripts/build/build_json.py

"""
构建 .json 规则集。
"""

import json
from pathlib import Path

from scripts.config import CLEAN_ROOT, PROJECT_ROOT, DOMAIN_RULESETS, IP_RULESETS, CUSTOM_ROOT
from scripts.utils.file_io import read_lines
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

REGEXP_PREFIX = "regexp:"
CUSTOM_PREFIX = "custom/"


def resolve_input_path(rel: str) -> Path:
    if rel.startswith(CUSTOM_PREFIX):
        return CUSTOM_ROOT / rel[len(CUSTOM_PREFIX):]
    return CLEAN_ROOT / rel


def load_domain_file(path: Path) -> tuple[set[str], set[str]]:
    domains: set[str] = set()
    regexps: set[str] = set()
    if not path.exists():
        logger.warning(f"{path} 不存在，跳过。")
        return domains, regexps
    for line in read_lines(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(REGEXP_PREFIX):
            regexps.add(line[len(REGEXP_PREFIX):])
        else:
            domains.add(line)
    return domains, regexps


def build_domain_json(output_name: str, inputs: list[str]) -> None:
    domains: set[str] = set()
    regexps: set[str] = set()
    for rel in inputs:
        d, r = load_domain_file(resolve_input_path(rel))
        domains.update(d)
        regexps.update(r)

    if not domains and not regexps:
        logger.warning(f"{output_name} 无可用规则，跳过。")
        return
    rules: list[dict] = []
    if domains:
        rules.append({"domain_suffix": sorted(domains)})
    if regexps:
        rules.append({"domain_regex": sorted(regexps)})
    rule_set = {
        "version": 5,
        "rules": rules
    }
    output_path = PROJECT_ROOT / f"{output_name}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(rule_set, f, ensure_ascii=False, indent=2)
    logger.info(f"{output_name}.json 已生成（domain={len(domains)}, regex={len(regexps)}）")


def build_ip_json(output_name: str, inputs: list[str]) -> None:
    cidrs: list[str] = []
    seen: set[str] = set()
    for rel in inputs:
        path = resolve_input_path(rel)
        if not path.exists():
            logger.warning(f"{path} 不存在，跳过。")
            continue
        for line in read_lines(path):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line not in seen:
                seen.add(line)
                cidrs.append(line)
    if not cidrs:
        logger.warning(f"{output_name} 无可用规则，跳过。")
        return
    rule_set = {
        "version": 5,
        "rules": [
            {
                "ip_cidr": cidrs
            }
        ]
    }
    output_path = PROJECT_ROOT / f"{output_name}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(rule_set, f, ensure_ascii=False, indent=2)
    logger.info(f"{output_name}.json 已生成（cidr={len(cidrs)}）")


def build_all_json() -> None:
    logger.info("开始生成 .json 规则集...")
    for name, inputs in DOMAIN_RULESETS.items():
        build_domain_json(name, inputs)
    for name, inputs in IP_RULESETS.items():
        build_ip_json(name, inputs)
    logger.info("所有 .json 规则集已生成！")
