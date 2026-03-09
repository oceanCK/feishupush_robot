"""
打字机效果线程模块
模拟键盘输入，更像真人打字
"""
import random
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

# 尝试导入pynput用于模拟键盘输入
try:
    from pynput.keyboard import Controller as KeyboardController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("警告: pynput未安装，键盘模拟功能将不可用。请运行: pip install pynput")


class TypewriterThread(QThread):
    """打字机效果线程 - 模拟键盘输入，更像真人打字"""
    text_signal = pyqtSignal(str)  # 用于更新显示
    char_signal = pyqtSignal(str)  # 用于发送单个字符
    countdown_signal = pyqtSignal(str)  # 用于发送倒计时信息
    
    def __init__(self, texts, auto_open_notepad=True):
        super().__init__()
        self.texts = texts
        self.running = False
        self.keyboard = KeyboardController() if PYNPUT_AVAILABLE else None
        self.auto_open_notepad = auto_open_notepad
        self.notepad_process = None
        self._check_interval = 50  # 每50ms检查一次running状态
        
        # ========== 打字速度配置（毫秒）==========
        # 字符间隔 - 模拟真人打字速度波动
        self.min_delay = 80       # 最快打字速度
        self.max_delay = 350      # 最慢打字速度（思考时）
        
        # 打字中途停顿（模拟思考下一个字）
        self.pause_chance = 0.12   # 12%概率停顿思考
        self.pause_min = 800       # 停顿最小时间
        self.pause_max = 3000      # 停顿最大时间（3秒）
        
        # 句子完成后的等待
        self.sentence_pause_min = 5000    # 句子完成后最小等待（5秒）
        self.sentence_pause_max = 15000   # 句子完成后最大等待（15秒）
        
        # 长时间休息（模拟人去做其他事情）
        self.rest_chance = 0.15    # 15%概率在句子之间休息更长时间
        self.rest_min = 30000      # 休息最小时间（30秒）
        self.rest_max = 120000     # 休息最大时间（2分钟）
        
        # 偶尔完全停止一段时间（模拟离开）
        self.long_break_chance = 0.02  # 2%概率长时间离开
        self.long_break_min = 180000   # 长休息最小（3分钟）
        self.long_break_max = 240000   # 长休息最大（4分钟）
    
    def open_notepad(self):
        """打开记事本并让它处于前台"""
        try:
            # 启动记事本
            self.notepad_process = subprocess.Popen(['notepad.exe'])
            # 等待记事本窗口启动（可中断）
            self.interruptible_sleep(800)
            self.text_signal.emit("[已打开记事本，开始模拟输入...]")
            return True
        except Exception as e:
            self.text_signal.emit(f"[无法打开记事本: {e}]")
            return False
    
    def interruptible_sleep(self, ms):
        """可中断的睡眠，每隔一小段时间检查running状态"""
        elapsed = 0
        while elapsed < ms and self.running:
            sleep_time = min(self._check_interval, ms - elapsed)
            self.msleep(sleep_time)
            elapsed += sleep_time
        return self.running  # 返回是否仍在运行
    
    def countdown_sleep(self, ms, prefix="等待"):
        """带倒计时显示的可中断睡眠"""
        elapsed = 0
        while elapsed < ms and self.running:
            remaining_ms = ms - elapsed
            remaining_seconds = (remaining_ms + 999) // 1000  # 向上取整
            
            # 每秒更新一次倒计时
            countdown_msg = f"[{prefix}中，剩余{remaining_seconds}秒...]"
            self.countdown_signal.emit(countdown_msg)
            
            # 睡眠1秒或剩余时间，取较小者
            sleep_time = min(1000, remaining_ms)
            self.msleep(sleep_time)
            elapsed += sleep_time
        
        return self.running
    
    def get_char_delay(self, char):
        """根据字符类型返回不同的随机延迟"""
        # 标点符号后停顿较久（像在思考下一句话）
        if char in '，。！？；：、,.:;!?':
            return random.randint(400, 800)
        # 空格相对快一点
        elif char == ' ':
            return random.randint(60, 150)
        # 换行后稍作停顿
        elif char == '\n':
            return random.randint(300, 600)
        # 普通字符 - 随机波动模拟真人
        else:
            # 使用正态分布让大多数在中间值附近，偶尔快或慢
            base = random.gauss(180, 60)  # 均值180ms，标准差60ms
            return max(self.min_delay, min(self.max_delay, int(base)))
    
    def run(self):
        self.running = True
        text_index = 0
        
        # 自动打开记事本
        if self.auto_open_notepad:
            if not self.open_notepad():
                self.text_signal.emit("[记事本打开失败，继续模拟输入...]")
            if not self.interruptible_sleep(500):
                return
        
        while self.running:
            if not self.texts:
                if not self.interruptible_sleep(100):
                    break
                continue
            
            current_text = self.texts[text_index % len(self.texts)]
            display_text = ""
            
            # 逐字输出
            for i, char in enumerate(current_text):
                if not self.running:
                    break
                
                display_text += char
                self.text_signal.emit(display_text)
                
                # 模拟键盘输入 - 真实输入到前台窗口
                if self.keyboard:
                    try:
                        self.keyboard.type(char)
                    except Exception as e:
                        print(f"键盘模拟错误: {e}")
                
                # 随机字符延迟（可中断）
                delay = self.get_char_delay(char)
                if not self.interruptible_sleep(delay):
                    break
                
                # 随机停顿思考（模拟人在想下一个字）
                if random.random() < self.pause_chance:
                    pause_time = random.randint(self.pause_min, self.pause_max)
                    self.text_signal.emit(display_text + " |")  # 显示光标闪烁效果
                    if not self.interruptible_sleep(pause_time):
                        break
            
            if self.running:
                # 输入换行，准备下一句 (暂时不模拟按下回车键，避免不必要的信息输出)
                # if self.keyboard:
                #     try:
                #         self.keyboard.type('\n')
                #     except:
                #         pass
                
                # 决定休息多长时间
                rand_val = random.random()
                
                if rand_val < self.long_break_chance:
                    # 长时间离开（3-5分钟）
                    break_time = random.randint(self.long_break_min, self.long_break_max)
                    self.text_signal.emit(f"{display_text}\n\n[即将离开一会儿...]")
                    if not self.countdown_sleep(break_time, "离开"):
                        break
                elif rand_val < self.long_break_chance + self.rest_chance:
                    # 中等休息时间（30秒-2分钟）
                    rest_time = random.randint(self.rest_min, self.rest_max)
                    self.text_signal.emit(f"{display_text}\n\n[即将休息...]")
                    if not self.countdown_sleep(rest_time, "休息"):
                        break
                else:
                    # 正常句子间隔（5-15秒）
                    wait_time = random.randint(self.sentence_pause_min, self.sentence_pause_max)
                    if not self.interruptible_sleep(wait_time):
                        break
                
                text_index += 1
    
    def stop(self):
        self.running = False
        # 注意：不关闭记事本，让用户可以看到输入的内容


def is_pynput_available():
    """检查pynput是否可用"""
    return PYNPUT_AVAILABLE
