"""
QA任务进度提醒工具
使用PyQt5实现的Windows应用程序

程序入口文件
"""
import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from main_window import MainWindow
from utils import get_icon_path
from auth_dialog import check_authorization


def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置应用程序图标（在任务栏中显示）
    # 使用 get_icon_path 支持打包后的路径
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 检查授权验证
    if not check_authorization():
        # 验证失败或用户取消，退出程序
        sys.exit(0)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
