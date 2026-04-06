#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 测试脚本 - 用于验证后端 API 功能

运行方式：python tests_api.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests

BASE_URL = "http://127.0.0.1:8000/api"


def test_send_verification():
    """测试发送验证码"""
    print("\n=== 测试：发送验证码 ===")
    response = requests.post(f"{BASE_URL}/auth/send-verification/", json={"phone": "13900000000"})
    print(f"状态码：{response.status_code}")
    print(f"响应：{response.json()}")


def test_list_companies():
    """测试企业搜索"""
    print("\n=== 测试：搜索企业 ===")
    response = requests.get(f"{BASE_URL}/list/companies/search/?q=科技")
    print(f"状态码：{response.status_code}")
    print(f"响应：{response.json()}")


def test_get_ranking():
    """获取榜单排行"""
    print("\n=== 测试：获取排行榜 ===")
    response = requests.get(f"{BASE_URL}/list/ranking/")
    print(f"状态码：{response.status_code}")
    print(f"响应：{response.json()}")


def main():
    """主函数"""
    print("🚀 API 测试开始...\n")

    try:
        test_list_companies()
        test_get_ranking()
        # test_send_verification()  # 需要先启动服务
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保已启动 Django 服务器：python manage.py runserver")


if __name__ == "__main__":
    main()
