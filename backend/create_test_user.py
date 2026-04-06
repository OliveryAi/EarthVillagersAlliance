from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser

class Command(BaseCommand):
    help = '创建测试管理员账号'

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('成功创建测试管理员账号：admin / admin123')
        else:
            self.stdout.write('管理员账号已存在')
