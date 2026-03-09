"""
主窗口模块
实现应用程序的主界面
"""
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QLabel, QFrame, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from clock_widget import ClockWidget
from typewriter_thread import TypewriterThread, is_pynput_available
from push_thread import PushThread
from utils import get_icon_path


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QA任务进度提醒工具")
        self.setMinimumSize(700, 400)
        self.resize(800, 450)
        
        # 设置窗口图标
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            print(icon_path)
            self.setWindowIcon(QIcon(icon_path))
        
        self.file_path = ""
        self.push_interval = 300  # 默认推送间隔（秒），5分钟
        self.push_thread = None
        self.typewriter_thread = None
        self.sample_texts = [       
            "给自己一点牛马激励：",
            "1、或许不安或许迷惑，但迷雾遮挡不住前方的光亮，有梦可待。",
            "2、愿所有为梦想而努力的人，都能吃到那颗糖。",
            "3、开心一点，努力一点，现实一点，善良一点，优秀一点。",
            "4、现在做的所有一切都是为了遇见一个更好的自己，不幽怨，不自卑，仿佛就充满了无限动力。",
            "5、不论是谁都应该活成自己想要的样子，一辈子只有一次，为什么不好好活一次。",
            "6、我会对生活满怀期待，对生命充满敬畏，加油坚持下去，生活是温暖而美好的！",
            "7、路过人间几十年，尽力做自己能做的事，不白来这一趟。",
            "8、足够正能量，有更高的格局和眼界。有的时候，只是胜负欲或是遗憾罢了。有舍才有得，相信缘分，一切都是最好的选择。",
            "9、事事岂能皆如人意，丧的一天又开始了，学会调整心态。",
            "10、让说话变成寓言，简单过好日子，脚下的路踩实了走。",
            "11、迷茫时，说明我依然热爱生活。失落时，证明我还有理想。即使还未完成也仍旧在路上。",
            "12、要相信世界是美好的，没有什么是过不去的，包括你，以后要对自己好一点，世界这么大，我还没逛够。",
            "13、一切都会变好的，我们不能去等，而是要自己去争取！",
            "14、路还在继续，梦还在期许。天高云远，至少看得见。",
            "15、看到美好，感受美好，屏蔽阴霾！",
            "16、近朱者赤近墨者黑，余生，做个有正能量的人。",
            "17、当你的前途一片黑暗时，你该意识到是你在发光。",
            "18、明天总会到来，太阳总会降临，光芒也是一样，闪闪发亮的你发现自己的可爱了吗？",
            "19、这个世界上，或许大多的事情不会如你所满意，而你真正要做的是把不喜欢的，努力做好。",
            "20、希望我爱的男孩能一直想着初心，向着光明，我们一起加油！",
            "21、生活中就是揉进去了很多元素成分，只有努力努力，才能看到成绩。",
            "22、这世间有人光万丈，有人一身锈，但总有人努力生活着。",
            "23、人间值得，虽然辛苦，但是滚烫。",
            "24、每一个人都有自己会得到的温柔，希望你自己有一双会发现的眼睛。",
            "25、活着才能改变，世界很大，你还没看呢。",
            "26、没人向你张开双臂，也要拥抱自己呀。",
            "27、世界不好也不坏，总有人悄悄爱着你。",
            "28、总会有一道光去照亮你，不过只是时间问题，人走茶未必会凉的哦。",
            "29、定期清空心里的垃圾，每天给自己一个开心的理由。",
            "30、永远相信自己的价值呀！任何人都是独立的个体，我们要自己认可自己，加油！",
            "聚焦当前工作，保持高效！当天任务可配置机器人通知进行信息推送",
            "保持专注，完成每一个任务！当天任务可配置机器人通知进行信息推送",
        ]
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== 左侧区域 =====
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_frame)
        
        # 标题
        left_title = QLabel("任务配置")
        left_title.setFont(QFont('微软雅黑', 12, QFont.Bold))
        left_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(left_title)
        
        # 文件路径显示
        self.file_display = QTextEdit()
        self.file_display.setPlaceholderText("点击下方按钮选择任务配置文件...\n\n支持JSON格式:\n[\n  {\"task\": \"任务名\", \"priority\": \"高\", \"status\": \"进行中\"},\n  ...\n]\n\n或纯文本格式（每行一个任务）")
        self.file_display.setReadOnly(True)
        left_layout.addWidget(self.file_display)
        
        # 选择文件按钮
        self.browse_btn = QPushButton("📁 选择文件")
        self.browse_btn.clicked.connect(self.browse_file)
        left_layout.addWidget(self.browse_btn)
        
        # 推送间隔设置
        interval_layout = QHBoxLayout()
        interval_label = QLabel("推送间隔(分钟):")
        interval_label.setFont(QFont('微软雅黑', 10))
        interval_layout.addWidget(interval_label)
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 1440)  # 1分钟到24小时
        self.interval_spinbox.setValue(5)  # 默认5分钟
        self.interval_spinbox.setSuffix(" 分钟")
        self.interval_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        self.interval_spinbox.valueChanged.connect(self.on_interval_changed)
        interval_layout.addWidget(self.interval_spinbox)
        left_layout.addLayout(interval_layout)
        
        # 开始/停止按钮
        self.start_btn = QPushButton("▶ 开始推送")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_btn.clicked.connect(self.toggle_push)
        self.start_btn.setEnabled(False)
        left_layout.addWidget(self.start_btn)
        
        main_layout.addWidget(left_frame, 1)
        
        # ===== 右侧区域 =====
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        
        # 时钟
        self.clock = ClockWidget()
        right_layout.addWidget(self.clock, 2)
        
        # 输出区域标题
        output_title = QLabel("即将推送的内容")
        output_title.setFont(QFont('微软雅黑', 10))
        output_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(output_title)
        
        # 输出框
        self.output_display = QTextEdit()
        self.output_display.setPlaceholderText("等待输出...")
        self.output_display.setReadOnly(True)
        self.output_display.setMaximumHeight(100)
        right_layout.addWidget(self.output_display)
        
        # 字符输出控制按钮
        self.output_btn = QPushButton("⌨ 任务内容输出")
        self.output_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.output_btn.clicked.connect(self.toggle_output)
        right_layout.addWidget(self.output_btn)
        
        # pynput状态提示
        if not is_pynput_available():
            warning_label = QLabel("⚠ pynput未安装，输出不可用")
            warning_label.setStyleSheet("color: orange;")
            right_layout.addWidget(warning_label)
        
        main_layout.addWidget(right_frame, 1)
    
    def browse_file(self):
        """浏览选择本地文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择任务配置文件",
            "",
            "所有文件 (*);;JSON文件 (*.json);;文本文件 (*.txt)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_display.setText(f"已选择文件:\n{file_path}")
            self.start_btn.setEnabled(True)
            
            # 读取文件内容预览
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.file_display.append("\n--- 文件内容预览 ---\n")
                    self.file_display.append(content[:500] + ("..." if len(content) > 500 else ""))
            except Exception as e:
                self.file_display.append(f"\n读取失败: {e}")
    
    def toggle_push(self):
        """切换推送状态"""
        if self.push_thread is not None and self.push_thread.isRunning():
            # 停止推送
            self.file_display.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] 正在停止推送服务...")
            self.push_thread.stop()
            # 等待线程结束，最多等待3秒
            if not self.push_thread.wait(3000):
                self.push_thread.terminate()  # 强制终止
                self.push_thread.wait(1000)
            self.push_thread = None
            self.start_btn.setText("▶ 开始推送")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            # 停止后重新启用间隔设置
            self.interval_spinbox.setEnabled(True)
        else:
            # 开始推送
            if not self.file_path:
                return
            
            # 使用用户设置的推送间隔（分钟转换为秒）
            interval_seconds = self.interval_spinbox.value() * 60
            self.push_thread = PushThread(self.file_path, interval=interval_seconds)
            self.push_thread.result_signal.connect(self.on_push_result)
            self.push_thread.start()
            
            # 推送开始后禁用间隔设置
            self.interval_spinbox.setEnabled(False)
            
            self.start_btn.setText("⏹ 停止推送")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
    
    def on_push_result(self, message):
        """推送结果回调"""
        self.file_display.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def on_interval_changed(self, value):
        """推送间隔改变回调"""
        self.push_interval = value * 60  # 转换为秒
    
    def toggle_output(self):
        """切换字符输出状态"""
        if self.typewriter_thread and self.typewriter_thread.running:
            # 停止输出
            self.typewriter_thread.stop()
            # 等待线程结束，最多等待200ms（因为使用了可中断睡眠，应该很快响应）
            if not self.typewriter_thread.wait(200):
                self.typewriter_thread.terminate()  # 强制终止
                self.typewriter_thread.wait(100)
            self.typewriter_thread = None
            self.output_btn.setText("⌨ 开始任务内容输出")
            self.output_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.output_display.clear()
        else:
            # 开始输出
            texts = self.sample_texts
            if self.push_thread and self.push_thread.tasks:
                texts = [t.get('task', '') for t in self.push_thread.tasks if t.get('task')]
            
            self.typewriter_thread = TypewriterThread(texts)
            self.typewriter_thread.text_signal.connect(self.update_output)
            self.typewriter_thread.countdown_signal.connect(self.update_output)
            self.typewriter_thread.start()
            
            self.output_btn.setText("⏹ 停止任务内容输出")
            self.output_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff9800;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #f57c00;
                }
            """)
    
    def update_output(self, text):
        """更新输出显示"""
        self.output_display.setText(text)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止所有线程
        if self.push_thread:
            self.push_thread.stop()
            self.push_thread.wait()
        
        if self.typewriter_thread:
            self.typewriter_thread.stop()
            self.typewriter_thread.wait()
        
        event.accept()
