"""
授权验证对话框
用于首次启动时的密码验证
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from auth import get_auth_manager


class AuthDialog(QDialog):
    """授权验证对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = get_auth_manager()
        self.is_verified = False
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("软件授权验证")
        self.setFixedSize(400, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("QA任务提醒工具")
        title_label.setFont(QFont('微软雅黑', 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 机器码显示
        machine_frame = QFrame()
        machine_layout = QVBoxLayout(machine_frame)
        machine_layout.setContentsMargins(0, 0, 0, 0)
        
        machine_title = QLabel("本机机器码：")
        machine_title.setFont(QFont('微软雅黑', 9))
        machine_layout.addWidget(machine_title)
        
        self.machine_code_label = QLabel(self.auth_manager.get_machine_code())
        self.machine_code_label.setFont(QFont('Consolas', 11, QFont.Bold))
        self.machine_code_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        self.machine_code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        machine_layout.addWidget(self.machine_code_label)
        
        layout.addWidget(machine_frame)
        
        # 密码输入
        password_frame = QFrame()
        password_layout = QVBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        password_title = QLabel("请输入授权码：")
        password_title.setFont(QFont('微软雅黑', 9))
        password_layout.addWidget(password_title)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("输入授权码后按回车或点击验证")
        self.password_input.setFont(QFont('微软雅黑', 10))
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.verify)
        password_layout.addWidget(self.password_input)
        
        layout.addWidget(password_frame)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.verify_btn = QPushButton("验证授权")
        self.verify_btn.setFont(QFont('微软雅黑', 10))
        self.verify_btn.setMinimumHeight(35)
        self.verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.verify_btn.clicked.connect(self.verify)
        
        self.cancel_btn = QPushButton("退出")
        self.cancel_btn.setFont(QFont('微软雅黑', 10))
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c21807;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.verify_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # 提示信息
        hint_label = QLabel("每个授权码仅限使用一次，验证通过后本机将自动记住授权状态")
        hint_label.setFont(QFont('微软雅黑', 8))
        hint_label.setStyleSheet("color: #888;")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
    
    def verify(self):
        """验证授权码"""
        code = self.password_input.text().strip()
        
        if not code:
            QMessageBox.warning(self, "提示", "请输入授权码！")
            self.password_input.setFocus()
            return
        
        is_valid, error_msg = self.auth_manager.verify_code(code)
        
        if is_valid:
            # 授权码有效，保存授权
            if self.auth_manager.save_authorization(code):
                self.is_verified = True
                QMessageBox.information(self, "成功", "授权验证成功！")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "保存授权信息失败，请检查权限！")
        else:
            QMessageBox.warning(self, "验证失败", f"{error_msg}，请重新输入！")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def get_verified(self):
        """返回是否验证成功"""
        return self.is_verified


def check_authorization():
    """
    检查授权状态
    返回: True - 已授权或验证成功, False - 未授权且验证失败
    """
    auth_manager = get_auth_manager()
    
    # 检查是否已授权
    if auth_manager.is_authorized():
        return True
    
    # 未授权，显示验证对话框
    dialog = AuthDialog()
    result = dialog.exec_()
    
    return result == QDialog.Accepted and dialog.get_verified()
