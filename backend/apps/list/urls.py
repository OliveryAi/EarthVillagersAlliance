from django.urls import path
from .views import CompanySearchView

urlpatterns = [
    # 注意：使用 lister 替代 list，避免与 Python 关键字冲突
    path('lister/companies/search/', CompanySearchView.as_view(), name='company_search'),
]
