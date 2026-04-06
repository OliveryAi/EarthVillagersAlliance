# List app models - 可扩展用于榜单管理功能

from django.db import models


class CategoryManagement(models.Model):
    """榜单分类管理"""
    name = models.CharField(max_length=100, verbose_name='榜单名称')
    slug = models.SlugField(unique=True, verbose_name='分类标识')
    description = models.TextField(blank=True, verbose_name='说明')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category_management'
        verbose_name = '榜单分类管理'
        verbose_name_plural = '榜单分类管理'
