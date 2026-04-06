"""
用户认证视图 - 手机注册、登录
"""
import hashlib
from datetime import timedelta, datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .models import CustomUser, VerificationCode
from config.settings import ADMIN_ACCOUNT


class RegisterView(APIView):
    """手机 + 验证码注册"""
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone', '')
        code = request.data.get('code', '')
        password = request.data.get('password', '')

        # 验证手机号格式
        if not phone_number or len(phone_number) != 11:
            return Response({'error': '请输入有效的 11 位手机号'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证验证码
        verification = VerificationCode.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False,
            expires_at__gte=timezone.now()
        ).first()

        if not verification:
            return Response({'error': '验证码错误、已过期或已使用'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查手机号是否已注册
        if CustomUser.objects.filter(_phone_encrypted__isnull=False).exists():
            existing = CustomUser.objects.filter(
                _phone_encrypted=CipherUtil.encrypt(phone_number)
            ).first()
            if existing:
                return Response({'error': '该手机号已注册'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建用户
        user = CustomUser.objects.create_user(username=phone_number, password=password)
        user.set_phone(phone_number)
        user.is_verified = True
        user.save()

        # 标记验证码已使用
        verification.is_used = True
        verification.save()

        return Response({
            'message': '注册成功',
            'user_id': user.id,
            'username': phone_number,
        }, status=status.HTTP_201_CREATED)


def admin_user_check(username, password):
    """检查预置管理员账号"""
    import bcrypt
    if username != ADMIN_ACCOUNT['username']:
        return None
    hashed = ADMIN_ACCOUNT['password_hash'].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), hashed):
        from django.contrib.auth.models import AnonymousUser
        admin_user = AnonymousUser()
        admin_user.is_staff = True
        admin_user.is_superuser = True
        return admin_user
    return None


class LoginView(APIView):
    """登录"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        # 管理员账号验证
        admin_user = admin_user_check(username, password)
        if admin_user:
            return Response({
                'message': '登录成功',
                'user_id': -1,  # -1 表示是预置管理员
                'is_admin': True,
            })

        user = CustomUser.objects.filter(username=username).first()

        if not user:
            return Response({'error': '用户不存在'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': '密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

        # 创建 Token - 关联到 native User，但记录 CustomUser ID 映射
        from django.contrib.auth import get_user_model
        NativeUser = get_user_model()

        # 查找或创建关联的 native user
        native_user, created = NativeUser.objects.get_or_create(username=user.username)

        if not native_user.check_password(password):
            native_user.set_password(password)
            native_user.save()

        # 为 CustomUser 设置密码（同步）
        user.set_password(password)
        user.save()

        # 创建 Token
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=native_user)

        return Response({
            'message': '登录成功',
            'user_id': user.id,
            'is_admin': False,
            'token': token.key,
        })


# 为 CustomUser 生成专属认证令牌（用于投票 API）
class GenerateCustomTokenView(APIView):
    """为 CustomUser 生成专用 token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # 检查是否有 CustomUser 关联的 token
        from rest_framework.authtoken.models import Token
        custom_token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': custom_token.key,
            'user_id': user.id,
        })


class PhoneVerificationRequestView(APIView):
    """请求验证码"""
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone', '')

        if not phone_number or len(phone_number) != 11:
            return Response({'error': '请输入有效的 11 位手机号'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已注册
        if CustomUser.objects.filter(username=phone_number).exists():
            return Response({'error': '该手机号已注册，请直接登录'})

        # 生成验证码
        code = ''.join([str(__import__('random').randint(0, 9)) for _ in range(6)])
        expires_at = timezone.now() + timedelta(minutes=5)

        # 保存验证码
        VerificationCode.objects.filter(user__phone_number=phone_number).delete()  # 清空旧码

        user = CustomUser(username=phone_number)
        user.save()

        verification_code = VerificationCode.objects.create(
            user=user,
            phone_number=phone_number,
            code=code,
            expires_at=expires_at
        )

        # 在实际环境中这里应该发送短信，测试环境打印到控制台
        print(f"【验证码】{phone_number}: {code}")

        return Response({
            'message': f'验证码已发送至手机号（测试环境请查看控制台输出）: {phone_number}',
            'expires_in_seconds': 300,
        })


class CipherUtil:
    @staticmethod
    def encrypt(value):
        from config.settings import CIPHER
        if not value:
            return None
        encrypted = CIPHER.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')
