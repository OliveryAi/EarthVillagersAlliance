#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用 PyInstaller 打包桌面客户端为 exe

运行方式：python build_exe.py
或手动执行命令：
pyinstaller --windowed --onefile --name="地球村民监察互助联盟" main.py
"""
import os
import sys


def build_exe():
    """构建 exe 文件"""
    # 确保当前目录正确
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    print("=== 地球村民监察互助联盟 - Exe 打包工具 ===\n")

    print("请确保已安装依赖:")
    print("$ pip install PyQt6 requests pyinstaller")
    print("\n执行打包命令...")
    print("=" * 50)

    # 检查 PyQt6 是否已安装
    try:
        import PyQt6.QtCore
        print("[OK] PyQt6 已安装")
    except ImportError:
        print("[ERROR] PyQt6 未安装，请先执行：pip install PyQt6")
        return

    # 构建 PyInstaller 参数列表
    params = [
        '--windowed',      # 无控制台窗口
        '--onefile',       # 单个可执行文件
        '--clean',         # 清理临时文件
        '--name=地球村民监察互助联盟',
        'main.py'
    ]

    # 如果有图标文件则添加
    if os.path.exists('app.ico'):
        params.insert(-1, '--icon=app.ico')

    cmd = f'pyinstaller {" ".join(params)}'

    print(f"命令：{cmd}\n")

    # 执行打包
    exit_code = os.system(cmd)

    if exit_code == 0:
        print("\n" + "=" * 50)
        print("打包成功！exe 文件位于：dist/地球村民监察互助联盟.exe")
        print("=" * 50)
    else:
        print(f"\n[ERROR] 打包失败，退出码：{exit_code}")


if __name__ == "__main__":
    build_exe()
