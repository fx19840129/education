#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密和安全工具
"""

import hashlib
import hmac
import secrets
import base64
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..errors.exceptions import EducationSystemError


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.fernet = self._create_fernet()
    
    def _generate_secret_key(self) -> str:
        """生成密钥"""
        return Fernet.generate_key().decode()
    
    def _create_fernet(self) -> Fernet:
        """创建Fernet加密器"""
        try:
            # 从密钥派生加密密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'education_system_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
            return Fernet(key)
        except Exception as e:
            raise EducationSystemError(f"创建加密器失败: {e}")
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise EducationSystemError(f"加密失败: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            raise EducationSystemError(f"解密失败: {e}")
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """哈希密码"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # 使用PBKDF2进行密码哈希
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        hashed = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
        
        return {
            "hash": hashed,
            "salt": salt
        }
    
    def verify_password(self, password: str, hash_info: Dict[str, str]) -> bool:
        """验证密码"""
        try:
            expected_hash = self.hash_password(password, hash_info["salt"])["hash"]
            return hmac.compare_digest(expected_hash, hash_info["hash"])
        except Exception:
            return False
    
    def generate_api_key(self, length: int = 32) -> str:
        """生成API密钥"""
        return secrets.token_urlsafe(length)
    
    def generate_token(self, length: int = 64) -> str:
        """生成访问令牌"""
        return secrets.token_urlsafe(length)
    
    def create_hmac_signature(self, data: str, secret: str) -> str:
        """创建HMAC签名"""
        signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_hmac_signature(self, data: str, signature: str, secret: str) -> bool:
        """验证HMAC签名"""
        expected_signature = self.create_hmac_signature(data, secret)
        return hmac.compare_digest(signature, expected_signature)


class SecureConfigManager:
    """安全配置管理器"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption = encryption_manager
        self.encrypted_keys = set()
    
    def encrypt_sensitive_value(self, key: str, value: str) -> str:
        """加密敏感值"""
        encrypted_value = self.encryption.encrypt(value)
        self.encrypted_keys.add(key)
        return encrypted_value
    
    def decrypt_sensitive_value(self, key: str, encrypted_value: str) -> str:
        """解密敏感值"""
        if key not in self.encrypted_keys:
            raise EducationSystemError(f"键 '{key}' 未加密或不存在")
        
        return self.encryption.decrypt(encrypted_value)
    
    def is_encrypted(self, key: str) -> bool:
        """检查键是否已加密"""
        return key in self.encrypted_keys


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """验证密码强度"""
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["valid"] = False
            result["issues"].append("密码长度至少8个字符")
        else:
            result["score"] += 1
        
        if not any(c.isupper() for c in password):
            result["issues"].append("密码应包含大写字母")
        else:
            result["score"] += 1
        
        if not any(c.islower() for c in password):
            result["issues"].append("密码应包含小写字母")
        else:
            result["score"] += 1
        
        if not any(c.isdigit() for c in password):
            result["issues"].append("密码应包含数字")
        else:
            result["score"] += 1
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result["issues"].append("密码应包含特殊字符")
        else:
            result["score"] += 1
        
        if result["score"] < 3:
            result["valid"] = False
        
        return result
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """清理输入字符串"""
        import html
        # HTML转义
        sanitized = html.escape(input_str)
        # 移除潜在危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()
    
    @staticmethod
    def validate_api_key_format(api_key: str, provider: str) -> bool:
        """验证API密钥格式"""
        if not api_key:
            return False
        
        if provider.lower() == 'zhipu':
            return api_key.startswith('sk-') and len(api_key) >= 20
        elif provider.lower() == 'openai':
            return api_key.startswith('sk-') and len(api_key) >= 20
        elif provider.lower() == 'anthropic':
            return api_key.startswith('sk-ant-') and len(api_key) >= 20
        
        return len(api_key) > 10


# 全局加密管理器实例
encryption_manager = EncryptionManager()

def get_encryption_manager() -> EncryptionManager:
    """获取加密管理器实例"""
    return encryption_manager
