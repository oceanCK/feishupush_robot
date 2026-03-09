"""
时钟组件模块
实现一个圆形时钟的可视化显示
"""
import math
from datetime import datetime
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush


class ClockWidget(QWidget):
    """圆形时钟组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        
        # 定时器更新时钟
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # 每秒更新
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取组件大小
        width = self.width()
        height = self.height()
        side = min(width, height)
        
        # 设置坐标系
        painter.translate(width / 2, height / 2)
        painter.scale(side / 200, side / 200)
        
        # 绘制表盘背景
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.setPen(QPen(QColor(100, 100, 100), 3))
        painter.drawEllipse(-90, -90, 180, 180)
        
        # 绘制刻度
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        for i in range(12):
            painter.drawLine(0, -80, 0, -70)
            painter.rotate(30)
        
        # 绘制小时刻度数字
        painter.setFont(QFont('Arial', 10, QFont.Bold))
        for i in range(1, 13):
            angle = i * 30 - 90
            x = 60 * math.cos(math.radians(angle))
            y = 60 * math.sin(math.radians(angle))
            painter.drawText(int(x) - 7, int(y) + 5, str(i))
        
        # 获取当前时间
        now = datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second
        
        # 绘制时针
        painter.save()
        painter.rotate(30 * hour + minute / 2)
        painter.setPen(QPen(QColor(50, 50, 50), 4, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(0, 5, 0, -40)
        painter.restore()
        
        # 绘制分针
        painter.save()
        painter.rotate(6 * minute + second / 10)
        painter.setPen(QPen(QColor(80, 80, 80), 3, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(0, 5, 0, -55)
        painter.restore()
        
        # 绘制秒针
        painter.save()
        painter.rotate(6 * second)
        painter.setPen(QPen(QColor(200, 50, 50), 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(0, 10, 0, -65)
        painter.restore()
        
        # 绘制中心点
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(-5, -5, 10, 10)
        
        # 显示数字时间
        painter.resetTransform()
        painter.translate(width / 2, height / 2)
        painter.setFont(QFont('Arial', 12))
        painter.setPen(QColor(50, 50, 50))
        time_str = now.strftime("%H:%M:%S")
        painter.drawText(-35, 40, time_str)
