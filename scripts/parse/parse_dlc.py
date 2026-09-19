#!/usr/bin/env python3
# /scripts/parse/parse_dlc.py
"""
解析 domain-list-community (DLC) 数据。
- 支持 include + @属性过滤（多属性 AND）；
- 保留 regexp 到输出文件底部。
"""

from pathlib import Path

from scripts.config import RAW_ROOT, CLEAN_ROOT
from scripts.parse.common import clean_line, normalize_domain, is_valid_domain
from scripts.utils.file_io import ensure_dir
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

RAW_DLC_DIR = RAW_ROOT / "dlc"
CLEAN_DLC_DIR = CLEAN_ROOT / "dlc"
# (domains, regexps)
RuleSet = tuple[frozenset[str], frozenset[str]]
EMPTY: RuleSet = (frozenset(), frozenset())


def parse_dlc_line(line: str) -> tuple[str, str, frozenset[str]]:
    line = clean_line(line)
    if not line:
        return "", "", frozenset()
    tokens = line.split()
    head = tokens[0]
    attrs = frozenset(t[1:] for t in tokens[1:] if t.startswith('@') and len(t) > 1)
    if ':' in head:
        rtype, value = head.split(':', 1)
        if rtype not in ('domain', 'full', 'regexp', 'include'):
            rtype, value = 'domain', head
    else:
        rtype, value = 'domain', head
    return rtype, value.strip(), attrs


def parse_dlc_file(
        file_path: Path,
        all_files: dict,
        memo: dict,
        filter_attrs: frozenset[str] = frozenset(),
        stack: frozenset = frozenset(),
) -> RuleSet:
    cache_key = (file_path, filter_attrs)
    if cache_key in memo:
        return memo[cache_key]
    if file_path in stack:
        logger.warning(f"循环 include: {file_path.name}，跳过。")
        return EMPTY
    domains: set[str] = set()
    regexps: set[str] = set()
    new_stack = stack | {file_path}
    raw_count = valid_count = 0
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                raw_count += 1
                rtype, value, attrs = parse_dlc_line(line)
                if not rtype or not value:
                    continue
                if rtype == 'include':
                    if value not in all_files:
                        continue
                    sub_filter = attrs if attrs else filter_attrs
                    d, r = parse_dlc_file(
                        all_files[value], all_files, memo,
                        filter_attrs=sub_filter, stack=new_stack,
                    )
                    domains.update(d)
                    regexps.update(r)
                    continue
                # 属性过滤（AND 语义）
                if filter_attrs and not filter_attrs.issubset(attrs):
                    continue
                if rtype == 'regexp':
                    regexps.add(value)
                    valid_count += 1
                else:  # domain / full
                    normalized = normalize_domain(value)
                    if normalized and is_valid_domain(normalized):
                        domains.add(normalized)
                        valid_count += 1
                    else:
                        logger.debug(f"丢弃非法域名: {value}")
        result: RuleSet = (frozenset(domains), frozenset(regexps))
        memo[cache_key] = result
        logger.info(
            f"{file_path.name}（filter={set(filter_attrs) or '∅'}）原始 {raw_count} 行，命中 {valid_count} 条，"
            f"domain：{len(domains)}, regexp：{len(regexps)}"
        )
        return result
    except Exception as e:
        logger.error(f"{file_path.name} 解析失败，错误: {e}")
        memo[cache_key] = EMPTY
        return EMPTY


def save_dlc_rules(file_path: Path, rules: RuleSet) -> None:
    domains, regexps = rules
    lines: list[str] = sorted(domains)
    if regexps:
        lines.append("")
        lines.extend(f"regexp:{r}" for r in sorted(regexps))
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_dlc():
    if not RAW_DLC_DIR.exists():
        logger.error(f"{RAW_DLC_DIR} 目录不存在！")
        return
    ensure_dir(CLEAN_DLC_DIR)
    logger.info("开始解析 DLC 数据...")
    all_files = {f.stem: f for f in RAW_DLC_DIR.iterdir() if f.is_file()}
    memo: dict = {}
    total = 0
    for raw_file in sorted(RAW_DLC_DIR.iterdir()):
        if not raw_file.is_file():
            continue
        total += 1
        rules = parse_dlc_file(raw_file, all_files, memo)
        save_dlc_rules(CLEAN_DLC_DIR / f"{raw_file.stem}.txt", rules)
    logger.info(f"DLC 解析完成，共处理 {total} 个文件，输出至: {CLEAN_DLC_DIR}")