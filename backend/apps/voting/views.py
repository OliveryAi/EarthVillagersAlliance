"""
投票视图 - 提交投票、查看榜单排行、企业搜索和证据上传，含防刷票机制
"""
import hashlib
import os
from datetime import timedelta, datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum

from .models import Vote, Company, VoteCategory, VoteStatistics


def get_device_fingerprint(request):
    """生成设备指纹"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    fingerprint_str = f"{user_agent}|{accept_language}"
    return hashlib.md5(fingerprint_str.encode()).hexdigest()


class SubmitVoteView(APIView):
    """提交投票（含防刷票）"""
    permission_classes = [IsAuthenticated]

    # 单 IP/日最大投票次数限制
    RATE_LIMIT_PER_DAY = 3

    def post(self, request):
        user = request.user

        category = request.data.get('category', '')
        company_id = request.data.get('company_id')
        reason = request.data.get('reason', '').strip()

        # 验证分类
        valid_categories = [c[0] for c in VoteCategory.choices]
        if category not in valid_categories:
            return Response({'error': '无效的榜单分类'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证企业存在
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': '目标企业不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 将 native User (token auth) 转换为 CustomUser（通过 username）
        from apps.accounts.models import CustomUser
        from django.contrib.auth import get_user_model
        NativeUser = get_user_model()

        if isinstance(user, NativeUser):
            custom_user = CustomUser.objects.filter(username=user.username).first()
            if not custom_user:
                return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        else:
            custom_user = user

        # 防刷票：检查是否已投过（使用 voter_id）
        if Vote.objects.filter(voter_id=custom_user.id, category=category, company=company).exists():
            return Response({'error': '您已对该企业投过同类别票，不可重复投票'}, status=status.HTTP_400_BAD_REQUEST)

        # 防刷票：检查 IP/设备频率限制
        ip_address = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '')
        fingerprint = get_device_fingerprint(request)

        today_midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 检查今日投票数（按 IP）- 使用 custom_user.id
        daily_votes = Vote.objects.filter(
            voter_id=custom_user.id,
            category=category,
            ip_address__startswith=ip_address.split(',')[0],
            created_at__gte=today_midnight
        ).count()

        if daily_votes >= SubmitVoteView.RATE_LIMIT_PER_DAY:
            return Response({
                'error': f'今日投票次数已达上限 ({SubmitVoteView.RATE_LIMIT_PER_DAY} 次)，请明日继续',
                'remaining_today': 0,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 防刷票：检查是否重复提交（设备指纹+IP+ 企业）- 使用 custom_user
        duplicates = Vote.objects.filter(
            ip_address__startswith=ip_address.split(',')[0],
            device_fingerprint=fingerprint,
            company=company,
            created_at__gte=today_midnight
        ).count()

        if duplicates > 0:
            return Response({
                'error': '系统检测到疑似重复投票，请稍后再试或联系管理员',
                'duplicate_count': duplicates,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 创建投票（匿名）- 使用 custom_user
        vote = Vote.objects.create(
            category=category,
            company=company,
            voter=custom_user,
            reason=reason[:2000],
            device_fingerprint=fingerprint,
            ip_address=ip_address.split(',')[0] if ip_address else None,
            is_anonymous=True
        )

        # 更新统计数据
        SubmitVoteView.update_statistics()

        return Response({
            'message': '投票成功',
            'vote_id': vote.id,
            'remaining_today': SubmitVoteView.RATE_LIMIT_PER_DAY - daily_votes - 1,
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def update_statistics():
        """更新各榜单的统计排行"""
        from .models import VoteStatistics

        # 清空现有统计
        VoteStatistics.objects.all().delete()

        # 按分类统计
        for category_code, category_name in VoteCategory.choices:
            votes = Vote.objects.filter(category=category_code)
            total_votes = votes.aggregate(Sum('id'))['id__sum'] or 0

            if total_votes == 0:
                continue

            # 遍历所有企业统计票数
            for company in Company.objects.all():
                vote_count = votes.filter(company_id=company.id).count()
                if vote_count > 0:
                    rate = (vote_count / total_votes * 100)
                    VoteStatistics.objects.create(
                        category=category_code,
                        company=company,
                        total_votes=vote_count,
                        vote_rate=rate
                    )


class ListRankingView(APIView):
    """获取榜单排行"""
    permission_classes = [AllowAny]

    def get(self, request, category=None):
        # 未指定分类时返回所有列表
        if not category:
            stats = VoteStatistics.objects.all().order_by('category', '-vote_rate')[:50]
            return Response([
                {
                    'category': s.category,
                    'company_name': s.company.name,
                    'total_votes': s.total_votes,
                    'vote_rate': float(s.vote_rate),
                    'industry': s.company.industry or '',
                    'city': s.company.city or '',
                }
                for s in stats
            ])

        # 获取特定分类排行
        try:
            category_obj = VoteCategory(category)
        except ValueError:
            return Response({'error': '无效的榜单分类'}, status=status.HTTP_400_BAD_REQUEST)

        stats = VoteStatistics.objects.filter(category=category).order_by('-vote_rate')[:20]

        result = []
        for idx, s in enumerate(stats):
            result.append({
                'rank': idx + 1,
                'category': s.category,
                'company_name': s.company.name,
                'total_votes': s.total_votes,
                'vote_rate': float(s.vote_rate),
                'industry': s.company.industry or '',
                'city': s.company.city or '',
            })

        return Response({
            'category': category_obj.value,
            'category_name': category_obj.label,
            'rankings': result,
        })


class CompanySearchView(APIView):
    """企业查询"""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({'error': '请输入搜索关键词'}, status=status.HTTP_400_BAD_REQUEST)

        companies = Company.objects.filter(
            name__icontains=query
        )[:50]

        return Response([
            {
                'id': c.id,
                'name': c.name,
                'industry': c.industry or '',
                'city': c.city or '',
            }
            for c in companies
        ])


class EvidenceUploadView(APIView):
    """证据材料上传"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .models import Evidence

        vote_id = request.data.get('vote_id')

        if not vote_id:
            return Response({'error': '缺少投票 ID'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已上传过证据
        existing_evidence = Evidence.objects.filter(vote_id=vote_id).exists()
        if existing_evidence:
            return Response({
                'error': '该投票已上传过证据，不可重复提交',
                'vote_id': vote_id,
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户是否是该投票的创建者 - 使用 voter_id
        try:
            from apps.accounts.models import CustomUser
            from django.contrib.auth import get_user_model
            NativeUser = get_user_model()

            if isinstance(request.user, NativeUser):
                custom_user = CustomUser.objects.filter(username=request.user.username).first()
                if not custom_user:
                    return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
                voter_id = custom_user.id
            else:
                voter_id = request.user.id

            vote = Vote.objects.get(id=vote_id, voter_id=voter_id)
        except Vote.DoesNotExist:
            return Response({'error': '投票不存在或无权上传'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'查询失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'evidence_file' not in request.FILES:
            return Response({'error': '请提供证据文件'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['evidence_file']

        # 文件类型验证
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.docx']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            return Response({
                'error': f'不支持的文件格式，仅支持：{", ".join(allowed_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 文件大小验证（最大 5MB）
        MAX_SIZE = 5 * 1024 * 1024
        if file.size > MAX_SIZE:
            return Response({'error': '文件过大，最大不超过 5MB'}, status=status.HTTP_400_BAD_REQUEST)

        # 确定文件类型
        file_type = 'image' if ext in ['.jpg', '.jpeg', '.png'] else 'document'

        try:
            from django.core.files.storage import default_storage
            filename = f'evidence/{vote_id}/{file.name}'
            filepath = default_storage.save(filename, file)
            file_url = default_storage.url(filepath)

            # 创建证据记录
            Evidence.objects.create(
                vote=vote,
                file_path=file_url,
                file_type=file_type
            )

            return Response({
                'message': '证据上传成功',
                'vote_id': vote_id,
                'file_url': file_url,
                'file_type': file_type,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'上传失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
