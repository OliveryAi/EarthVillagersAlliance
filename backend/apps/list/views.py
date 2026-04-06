# List app views - 暂留空，未来可扩展榜单管理功能
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CompanySearchView(APIView):
    """企业查询（移至此处，避免 list 关键字冲突）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        from apps.voting.models import Company
        if not query:
            return Response({'error': '请输入搜索关键词'}, status=400)

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
