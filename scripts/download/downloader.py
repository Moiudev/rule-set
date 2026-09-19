#!/usr/bin/env python3
# /scripts/download/downloader.py

"""
通用下载器，支持重试机制、超时控制、日志记录。
"""

import time
from pathlib import Path

import requests

from scripts.utils.file_io import ensure_dir
from scripts.utils.logger import init_logger

logger = init_logger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; RuleSet-Builder/1.0)"
DOWNLOAD_TIMEOUT = 60
DOWNLOAD_RETRIES = 3
RETRY_BACKOFF = 3
CHUNK_SIZE = 8192


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT
    })
    return session


def download(url: str, save_path: Path, timeout: int = DOWNLOAD_TIMEOUT, retries: int = DOWNLOAD_RETRIES) -> bool:
    session = create_session()
    for attempt in range(1, retries + 1):
        try:
            ensure_dir(save_path.parent)
            logger.info(f"正在下载 {url}...")
            response = session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
            logger.info(f"{save_path.name} 下载成功！")
            return True
        except requests.RequestException as e:
            logger.warning(f"{url} 下载失败（尝试 {attempt}/{retries}），错误：{e}")
            if attempt < retries:
                wait = RETRY_BACKOFF * attempt
                logger.info(f"等待 {wait} 秒后重试...")
                time.sleep(wait)
        except Exception as e:
            logger.error(f"下载时发生未知错误：{e}，路径：{save_path}")
            break
    logger.error(f"下载 {url} 失败，已重试 {retries} 次！")
    return False