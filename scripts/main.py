#!/usr/bin/env python3
# /scripts/main.py

"""
sing-box 自定义规则集构建工具主入口。
"""
from scripts.build.build_json import build_all_json
from scripts.build.build_srs import build_all_srs
from scripts.download.download_dlc import download_dlc
from scripts.download.download_rules import download_all_rules
from scripts.download.download_singbox import download_and_install_singbox
from scripts.parse.parse_all import parse_all
from scripts.parse.parse_dlc import parse_dlc
from scripts.utils.logger import init_logger

logger = init_logger("main")


def main():
    logger.info("-------------------- 开始执行脚本 --------------------")

    try:
        logger.info("开始下载并安装 sing-box...")
        download_and_install_singbox()

        logger.info("准备下载规则源和 DLC...")
        download_all_rules()
        download_dlc()

        logger.info("准备解析规则源和 DLC...")
        parse_all()
        parse_dlc()

        logger.info("准备构建 .json 规则集...")
        build_all_json()

        logger.info("准备构建 .srs 规则集...")
        build_all_srs()

        logger.info("所有任务已完成！")
        logger.info("-------------------- 脚本执行结束 --------------------")

    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        raise


if __name__ == "__main__":
    main()