import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.voting.models import Company

# 创建测试企业（使用英文字母避免编码问题）
companies = [
    ('Tencent Tech', 'Internet', 'Shenzhen'),
    ('Alibaba Group', 'E-commerce', 'Hangzhou'),
    ('ByteDance', 'Technology', 'Beijing'),
    ('Huawei Technologies', 'Telecom Equipment', 'Shenzhen'),
]

for name, industry, city in companies:
    if not Company.objects.filter(name=name).exists():
        Company.objects.create(name=name, industry=industry, city=city)
        print(f'Created: {name}')

print(f'\nTotal companies: {Company.objects.count()}')
