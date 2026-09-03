#!/usr/bin/env python3
# /scripts/parse/parse_ip.py

"""
IP CIDR 解析，专门处理 [ip] 分组下的规则源。
"""

import ipaddress
from pathlib import Path

from scripts.config import CLEAN_ROOT
from scripts.parse.common import parse_group, save_sorted_rules
from scripts.utils.logger import init_logger

logger = init_logger(__name__)


def extract_cidr(line: str) -> str:
    try:
        return str(ipaddress.ip_network(line, strict=False))
    except ValueError:
        return ""


def is_valid_cidr(cidr: str) -> bool:
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False


def optimize_networks(networks: list) -> list:
    if not networks:
        return []
    networks.sort(key=lambda n: (n.network_address, n.prefixlen))
    optimized = []
    for net in networks:
        if not any(existing.supernet_of(net) for existing in optimized):
            optimized.append(net)
    return optimized


def optimize_cidrs(cidrs: set[str]) -> list[str]:
    logger.info(f"正在优化 IP CIDR，输入数量：{len(cidrs)}")
    v4_networks = []
    v6_networks = []
    for cidr in cidrs:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if network.version == 4:
                v4_networks.append(network)
            else:
                v6_networks.append(network)
        except ValueError:
            continue
    v4_opt = optimize_networks(v4_networks)
    v6_opt = optimize_networks(v6_networks)
    result = [str(net) for net in v4_opt + v6_opt]
    logger.info(f"IP 优化完成：v4={len(v4_opt)}, v6={len(v6_opt)}, total={len(result)}")
    return result


def sort_cidrs(cidrs: list[str]) -> list[str]:
    v4 = []
    v6 = []
    for cidr in cidrs:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if network.version == 4:
                v4.append(network)
            else:
                v6.append(network)
        except ValueError:
            continue
    v4_sorted = sorted(v4)
    v6_sorted = sorted(v6)
    result = [str(net) for net in v4_sorted + v6_sorted]
    logger.info(f"CIDR 排序完成：v4={len(v4_sorted)}, v6={len(v6_sorted)}")
    return result


def parse_ip_group(raw_dir: Path):
    all_rules = parse_group(raw_dir=raw_dir, extractor=extract_cidr, validator=is_valid_cidr)
    optimized = optimize_cidrs(all_rules)
    sorted_rules = sort_cidrs(optimized)
    save_sorted_rules(CLEAN_ROOT / "ip.txt", sorted_rules)