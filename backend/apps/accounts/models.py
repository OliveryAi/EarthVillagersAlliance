"""
用户认证模块 - 手机验证码注册与加密存储
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from config.settings import get_cipher

CIPHER = None  # Lazy loaded via get_cipher()


def _get_cipher():
    """获取加密器"""
    global CIPHER
    if CIPHER is None:
        CIPHER = get_cipher()
    return CIPHER


class EncryptedPhone(models.TextField):
    """手机号加密字段"""
    def encrypt_value(self, value):
        cipher = _get_cipher()
        if not value:
            return None
        encrypted = cipher.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')

    def decrypt_value(self, encrypted_value):
        cipher = _get_cipher()
        if not encrypted_value:
            return None
        decrypted = cipher.decrypt(encrypted_value.encode('utf-8'))
        return decrypted.decode('utf-8')


class CustomUser(AbstractUser):
    """自定义用户模型 - 手机注册"""
    # 手机号加密存储（手动 encrypt/decrypt）
    _phone_encrypted = models.TextField(verbose_name='加密后的手机号', blank=True, null=True)
    device_fingerprint = models.CharField(max_length=256, verbose_name='设备指纹', blank=True, help_text="用于防刷票")
    is_verified = models.BooleanField(default=False, verbose_name='是否已验证')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    class Meta:
        db_table = 'custom_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        # 解决与 AbstractUser 的 reverse accessor 冲突
        proxy = False

    # 覆盖 groups 和 user_permissions，添加新的 related_name 避免冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_groups',
        help_text='The groups this user belongs to.',
        related_query_name='custom_user'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_permissions',
        help_text='Specific permissions for this user.',
        related_query_name='custom_user'
    )

    @property
    def phone(self):
        """解密手机号"""
        return self.decrypt_phone(self._phone_encrypted) if self._phone_encrypted else None

    def set_phone(self, phone_number):
        """加密存储手机号"""
        cipher = _get_cipher()
        self._phone_encrypted = cipher.encrypt(phone_number.encode('utf-8'))

    @staticmethod
    def decrypt_phone(encrypted_value):
        """解密手机号"""
        if not encrypted_value:
            return None
        cipher = _get_cipher()
        decrypted = cipher.decrypt(encrypted_value.encode('utf-8'))
        return decrypted.decode('utf-8')

    def __str__(self):
        return f"User-{self.id}"


class VerificationCode(models.Model):
    """验证码表 - 临时存储"""
    PHONE_CODE_LENGTH = 6

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_codes')
    phone_number = models.CharField(max_length=15, verbose_name='手机号', blank=True)  # 明文仅用于验证时比对
    code = models.CharField(max_length=8, verbose_name='验证码')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'verification_code'
        verbose_name = '验证码'
        verbose_name_plural = '验证码'

    def __str__(self):
        return f"Code-{self.id} for {self.phone_number}"
