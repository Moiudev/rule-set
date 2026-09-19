#!/usr/bin/env python3
# /scripts/download/download_singbox.py

"""
下载 sing-box，支持自动获取最新版本、下载、解压、安装。
"""

import os
import sys
import tarfile
import tempfile
from pathlib import Path
from shutil import move

import requests

from scripts.download.downloader import download
from scripts.utils.file_io import ensure_dir
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

REQUEST_TIMEOUT = 30
BIN_PATH = "/usr/local/bin/sing-box"


def get_latest_asset():
    try:
        api_url = "https://api.github.com/repos/SagerNet/sing-box/releases/latest"
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        release = response.json()
        tag = release["tag_name"]
        for asset in release["assets"]:
            if "linux-amd64.tar.gz" in asset["name"]:
                logger.info(f"找到目标文件: {asset['name']}")
                return tag, asset["browser_download_url"]
        logger.error(f"在版本 {tag} 中未找到 linux-amd64.tar.gz！")
        sys.exit(1)
    except requests.RequestException as e:
        logger.error(f"GitHub API 请求失败，错误：{e}")
        sys.exit(1)


def extract_singbox(tar_path: Path, out_dir: Path) -> Path:
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(out_dir)
        logger.info(f"解压完成！")
        for root, _, files in os.walk(out_dir):
            for file in files:
                if file == "sing-box":
                    binary = Path(root) / file
                    logger.info(f"找到 sing-box 可执行文件: {binary}")
                    return binary
        logger.error("解压目录中未找到 sing-box 可执行文件！")
        sys.exit(1)
    except Exception as e:
        logger.error(f"解压 sing-box 失败，错误：{e}")
        sys.exit(1)


def download_and_install_singbox():
    try:
        tag, asset_url = get_latest_asset()
        logger.info(f"检测到最新版本: {tag}")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tar_path = tmp_path / "sing-box.tar.gz"
            logger.info("正在下载 sing-box...")
            if not download(asset_url, tar_path):
                logger.error("sing-box 下载失败！")
                sys.exit(1)
            logger.info("下载完成，正在解压...")
            binary = extract_singbox(tar_path, tmp_path)
            logger.info("正在安装 sing-box...")
            binary.chmod(0o755)
            ensure_dir(Path(BIN_PATH).parent)
            move(str(binary), BIN_PATH)
        logger.info(f"sing-box 安装完成！路径：{BIN_PATH}")
    except Exception as e:
        logger.error(f"安装 sing-box 失败，错误：{e}")
        sys.exit(1)