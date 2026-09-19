#!/usr/bin/env python3
# /scripts/utils/logger.py

"""
日志工具，格式: [时间] [级别] [模块] 消息。
"""

import logging
import sys


def init_logger(name: str = "rule_set", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger