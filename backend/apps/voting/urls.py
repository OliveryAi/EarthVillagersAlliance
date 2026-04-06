from django.urls import path
from .views import SubmitVoteView, ListRankingView, CompanySearchView, EvidenceUploadView

urlpatterns = [
    path('submit/', SubmitVoteView.as_view(), name='submit_vote'),
    path('ranking/', ListRankingView.as_view(), name='list_ranking'),
    path('ranking/<slug:category>/', ListRankingView.as_view(), name='category_ranking'),
    path('companies/search/', CompanySearchView.as_view(), name='company_search'),
    path('evidence/upload/', EvidenceUploadView.as_view(), name='evidence_upload'),
]

# 统一证据上传路由到 /api/vote/evidence/upload/
