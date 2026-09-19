#!/usr/bin/env python3
# /scripts/utils/file_io.py

"""
文件操作工具。
"""

from pathlib import Path
from typing import List, Set, Union

from scripts.utils.logger import init_logger

logger = init_logger(__name__)


def ensure_dir(directory: Path) -> Path:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"{directory} 目录已创建！")
        return directory
    except Exception as e:
        logger.error(f"创建 {directory} 目录失败，错误：{e}")
        raise


def read_lines(file_path: Path, encoding: str = "utf-8") -> List[str]:
    if not file_path.exists():
        logger.warning(f"{file_path.name} 文件不存在！")
        return []
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = [line.strip() for line in f if line.strip()]
        logger.debug(f"读取 {file_path.name} 文件成功！")
        return lines
    except Exception as e:
        logger.error(f"读取 {file_path.name} 文件失败！错误：{e}")
        return []


def write_lines(file_path: Path, lines: Union[List[str], Set[str]], encoding: str = "utf-8"):
    try:
        ensure_dir(file_path.parent)
        # 若传入的是 set，先转为 list
        if isinstance(lines, set):
            lines = list(lines)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write('\n'.join(lines) + '\n')
        logger.info(f"写入 {file_path.name} 文件成功！")
    except Exception as e:
        logger.error(f"写入 {file_path.name} 文件失败，错误：{e}")