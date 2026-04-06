import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.voting.models import Company


def main():
    # 创建企业
    companies_data = [
        {'name': '腾讯科技', 'industry': '互联网', 'city': '深圳'},
        {'name': '阿里巴巴', 'industry': '电商', 'city': '杭州'},
        {'name': '字节跳动', 'industry': '互联网', 'city': '北京'},
        {'name': '华为技术', 'industry': '通信设备', 'city': '深圳'},
        {'name': '网易', 'industry': '游戏/电商', 'city': '杭州'},
    ]

    created = 0
    for data in companies_data:
        if not Company.objects.filter(name=data['name']).exists():
            Company.objects.create(**data)
            created += 1

    print(f'成功创建 {created} 家企业数据')


if __name__ == '__main__':
    main()
