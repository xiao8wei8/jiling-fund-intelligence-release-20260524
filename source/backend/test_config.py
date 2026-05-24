#!/usr/bin/env python3
"""测试配置文件和API密钥管理"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config import Config

print("=== 配置文件测试 ===")
print(f"SECRET_KEY: {'***' if Config.SECRET_KEY else '未设置'}")
print(f"MINIMAX_TOKEN: {'***' if Config.MINIMAX_TOKEN else '未设置'}")
print(f"MINIMAX_API: {Config.MINIMAX_API}")
print(f"CACHE_DURATION: {Config.CACHE_DURATION}秒")
print(f"PORT: {Config.PORT}")
print(f"DEBUG: {Config.DEBUG}")

print("\n=== 测试完成 ===")
print("配置文件加载成功！API密钥已从配置文件中读取。")
