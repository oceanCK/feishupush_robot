"""
推送任务线程模块
负责定时推送任务到飞书
"""
import json
from PyQt5.QtCore import QThread, pyqtSignal

# 直接导入推送函数，避免启动子进程
from feishu_push import push_msg


class PushArgs:
    """模拟argparse的命名空间对象"""
    def __init__(self, name='None', task='None', priority='None', status='None'):
        self.name = name
        self.task = task
        self.priority = priority
        self.status = status


class PushThread(QThread):
    """推送任务线程"""
    result_signal = pyqtSignal(str)
    
    def __init__(self, file_path, interval=300):
        super().__init__()
        self.file_path = file_path
        self.interval = interval  # 推送间隔（秒）
        self._running = False
        self.tasks = []
        self.current_index = 0
    
    @property
    def running(self):
        return self._running
    
    def load_tasks(self):
        """从文件加载任务"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 尝试解析为JSON
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        self.tasks = data
                    else:
                        self.tasks = [data]
                except json.JSONDecodeError:
                    # 如果不是JSON，按行读取
                    lines = content.strip().split('\n')
                    self.tasks = [{"task": line, "priority": "中", "status": "进行中"} for line in lines if line.strip()]
            return True
        except Exception as e:
            self.result_signal.emit(f"加载文件失败: {e}")
            return False
    
    def run(self):
        self._running = True
        if not self.load_tasks():
            self._running = False
            return
        
        self.result_signal.emit("推送服务已启动")
        
        while self._running:
            if self.tasks and self._running:
                task = self.tasks[self.current_index % len(self.tasks)]
                self.push_task(task)
                self.current_index += 1
            
            # 等待指定间隔，每100ms检查一次是否需要停止
            for _ in range(self.interval * 10):
                if not self._running:
                    break
                self.msleep(100)
        
        self.result_signal.emit("推送服务已停止")
    
    def push_task(self, task):
        """直接调用推送函数推送任务（不再启动子进程）"""
        if not self._running:
            return
            
        try:
            name = task.get('name', 'None')
            task_name = task.get('task', 'None')
            priority = task.get('priority', 'None')
            status = task.get('status', 'None')
            
            # 创建参数对象
            args = PushArgs(
                name=name,
                task=task_name,
                priority=priority,
                status=status
            )
            
            # 直接调用推送函数
            push_msg(args)
            self.result_signal.emit(f"推送成功: {task_name}")
                
        except Exception as e:
            self.result_signal.emit(f"推送错误: {e}")
    
    def stop(self):
        """停止推送线程"""
        self._running = False
    
    def get_next_text(self):
        """获取下一条要推送的文本"""
        if self.tasks:
            return self.tasks[self.current_index % len(self.tasks)].get('task', '')
        return ''
