"""
工具函数模块
包含资源路径处理等通用功能
"""
import os
import sys


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    支持开发环境和PyInstaller打包后的环境
    """
    # PyInstaller 打包后的路径
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # 开发环境的路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def get_icon_path():
    """获取应用图标路径"""
    return get_resource_path('app_icon.ico')
