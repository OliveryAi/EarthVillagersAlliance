#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""初始化数据库和预置数据"""
import os
import sys
import django

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Add backend dir to path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from apps.accounts.models import CustomUser


def initialize():
    """初始化数据"""
    # 1. 创建管理员账户 (密码：110119120)
    admin_username = "11011912000"

    if CustomUser.objects.filter(username=admin_username).exists():
        print(f"[OK] 管理员账户已存在：{admin_username}")
    else:
        admin_user = CustomUser.objects.create_superuser(
            username=admin_username,
            password="110119120",
            email=""
        )
        print(f"[OK] 管理员账户已创建：{admin_username} / 110119120")

    # 2. 预置测试企业
    from apps.voting.models import Company
    test_companies = [
        ("示例科技有限公司", "互联网", "北京"),
        ("测试集团股份有限公司", "制造业", "上海"),
        ("演示餐饮有限公司", "服务业", "广州"),
        ("模拟贸易合伙企业", "商贸", "深圳"),
    ]

    for name, industry, city in test_companies:
        if not Company.objects.filter(name=name).exists():
            Company.objects.create(name=name, industry=industry, city=city)
            print(f"[OK] 已添加企业：{name}")

    # 3. 创建测试用户 (手机号 13800138000，密码 test123456)
    if CustomUser.objects.filter(username="13800138000").exists():
        print(f"[OK] 测试用户已存在：13800138000")
    else:
        test_user = CustomUser.objects.create_user(
            username="13800138000",
            password="test123456"
        )
        print(f"[OK] 测试用户已创建：13800138000 / test123456")

    print("\n=== 数据初始化完成 ===\n")
    print("可用操作:")
    print("1. 启动服务：python manage.py runserver")
    print("2. 访问 admin: http://localhost:8000/admin")


if __name__ == '__main__':
    initialize()
