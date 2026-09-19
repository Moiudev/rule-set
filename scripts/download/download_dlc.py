#!/usr/bin/env python3
# /scripts/download/download_dlc.py
"""
下载 domain-list-community (DLC) 数据。
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.config import RAW_ROOT
from scripts.utils.file_io import ensure_dir
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

DLC_REPO_URL = "https://github.com/v2fly/domain-list-community.git"
RAW_DLC_DIR = RAW_ROOT / "dlc"
TIMEOUT = 120


def download_dlc():
    logger.info("开始下载 domain-list-community (DLC)...")
    ensure_dir(RAW_DLC_DIR)
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        logger.info("正在克隆 DLC 仓库...")
        try:
            result = subprocess.run(
                ["git", "clone", "--depth=1", DLC_REPO_URL, str(tmp_dir)],
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )
            if result.returncode != 0:
                logger.error(f"克隆失败，错误: {result.stderr.strip()}")
                return False
        except Exception as e:
            logger.error(f"克隆过程异常: {e}")
            return False
        src_data_dir = tmp_dir / "data"
        if not src_data_dir.exists():
            logger.error("未找到 data 目录！")
            return False
        logger.info("正在复制 DLC 数据文件...")
        file_count = 0
        for file in src_data_dir.iterdir():
            if file.is_file():
                dest_file = RAW_DLC_DIR / f"{file.name}.txt"
                shutil.copy2(file, dest_file)
                logger.info(f"{file.name} 已保存。")
                file_count += 1

        logger.info(f"DLC 下载完成，共保存 {file_count} 个文件到 {RAW_DLC_DIR}。")
        return True