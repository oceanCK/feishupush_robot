"""
授权验证模块
实现机器码绑定 + 一次性授权码验证功能
"""
import hashlib
import uuid
import os
import json
from datetime import datetime


class AuthManager:
    """授权管理器"""
    
    # 一次性授权码列表（每个码只能使用一次）
    # hash - AES (Name+xiaohuang)
    AUTH_CODES = [
        "U2FsdGVkX192k5fZ4hQlZTmyIexWtCnurmer4PiBY94=", # L
        "U2FsdGVkX196tBXhycZVog/uNJ3dZXEOi45pCnO397c=", # Y
        "U2FsdGVkX19rI5G4Fc4bCivX3jFFloZzE9if+E3CiOc=", # Z
        "U2FsdGVkX19dtgky+ljFlEjYGCaE0JHAEFjF8rWRQzw=", # X
        "U2FsdGVkX18eNZkFffEYxC5ZhauE0S2Pxpl372IZ1VU=", # D
    ]
    
    # 授权配置文件名
    AUTH_FILE = ".auth_config"
    
    def __init__(self):
        self.machine_code = self._generate_machine_code()
        self.auth_file_path = self._get_auth_file_path()
        self.used_codes_path = self._get_used_codes_path()
    
    def _get_auth_file_path(self):
        """获取授权文件路径（放在用户目录下）"""
        user_home = os.path.expanduser("~")
        return os.path.join(user_home, ".qa_reminder_auth")
    
    def _get_used_codes_path(self):
        """获取已使用授权码记录文件路径"""
        # 放在程序同目录下，方便管理
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".used_codes")
    
    def _get_used_codes(self):
        """获取已使用的授权码列表"""
        if not os.path.exists(self.used_codes_path):
            return []
        try:
            with open(self.used_codes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('used_codes', [])
        except Exception:
            return []
    
    def _mark_code_as_used(self, code):
        """将授权码标记为已使用"""
        used_codes = self._get_used_codes()
        if code not in used_codes:
            used_codes.append(code)
        
        data = {
            'used_codes': used_codes,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            with open(self.used_codes_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def _generate_machine_code(self):
        """
        生成机器唯一标识码
        基于MAC地址 + 用户名生成
        """
        # 获取MAC地址
        mac = uuid.getnode()
        mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        
        # 获取用户名
        username = os.getenv('USERNAME') or os.getenv('USER') or 'unknown'
        
        # 组合并哈希
        combined = f"{mac_str}_{username}"
        hash_obj = hashlib.sha256(combined.encode())
        
        # 取前16位作为机器码（便于显示）
        return hash_obj.hexdigest()[:16].upper()
    
    def get_machine_code(self):
        """获取当前机器码"""
        return self.machine_code
    
    def is_authorized(self):
        """检查当前机器是否已授权"""
        if not os.path.exists(self.auth_file_path):
            return False
        
        try:
            with open(self.auth_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证机器码是否匹配
            stored_code = data.get('machine_code', '')
            if stored_code == self.machine_code:
                return True
            
            return False
        except Exception:
            return False
    
    def verify_code(self, code):
        """
        验证授权码
        返回: (是否有效, 错误信息)
        """
        code = code.strip()
        
        # 检查授权码是否在列表中
        if code not in self.AUTH_CODES:
            return False, "授权码无效"
        
        # 检查授权码是否已被使用
        used_codes = self._get_used_codes()
        if code in used_codes:
            return False, "此授权码已被使用"
        
        return True, None
    
    def save_authorization(self, used_code):
        """保存授权信息并标记授权码为已使用"""
        data = {
            'machine_code': self.machine_code,
            'auth_code': used_code,
            'auth_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0'
        }
        
        try:
            with open(self.auth_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 标记授权码为已使用
            self._mark_code_as_used(used_code)
            return True
        except Exception as e:
            print(f"保存授权信息失败: {e}")
            return False
    
    def revoke_authorization(self):
        """撤销授权（删除授权文件）"""
        if os.path.exists(self.auth_file_path):
            try:
                os.remove(self.auth_file_path)
                return True
            except Exception:
                return False
        return True


# 单例实例
_auth_manager = None

def get_auth_manager():
    """获取授权管理器单例"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
