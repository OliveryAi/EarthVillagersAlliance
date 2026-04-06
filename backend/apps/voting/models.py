"""
投票与榜单模型 - 四个观察榜
"""
from django.db import models


class VoteCategory(models.TextChoices):
    """投票分类定义"""
    AGE_DISCRIMINATION = 'age_discrimination', '35 岁以上就业歧视观察榜'
    GENDER_DISCRIMINATION = 'gender_discrimination', '性别歧视观察榜'
    PUA_DESPOTISM = 'pua_despotism', '职场 PUA 专制观察榜'
    OVERWORK_EXPLOITATION = 'overwork_exploitation', '职场过劳剥削观察榜'


class Company(models.Model):
    """企业信息表"""
    name = models.CharField(max_length=200, verbose_name='企业/单位名称')
    industry = models.CharField(max_length=100, blank=True, verbose_name='所属行业')
    city = models.CharField(max_length=100, blank=True, verbose_name='所在城市')
    description = models.TextField(blank=True, verbose_name='企业简介')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company'
        verbose_name = '企业'
        verbose_name_plural = '企业'

    def __str__(self):
        return self.name


class Vote(models.Model):
    """投票记录"""
    category = models.CharField(
        max_length=50,
        choices=VoteCategory.choices,
        db_index=True,
        verbose_name='榜单分类'
    )
    company = models.ForeignKey(Company, related_name='votes', on_delete=models.CASCADE, verbose_name='目标企业')
    voter = models.ForeignKey('accounts.CustomUser', related_name='votes', on_delete=models.CASCADE, verbose_name='投票用户')

    reason = models.TextField(verbose_name='投票理由/评价', max_length=2000)
    is_anonymous = models.BooleanField(default=True, verbose_name='是否匿名投票')

    # 防刷票字段
    device_fingerprint = models.CharField(max_length=256, verbose_name='设备指纹', help_text="浏览器指纹识别")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='投票时间')

    class Meta:
        db_table = 'vote'
        unique_together = ('category', 'company', 'voter')  # 同一用户对同一企业同类别只能投一次票
        verbose_name = '投票'
        verbose_name_plural = '投票'

    def __str__(self):
        return f"Vote-{self.id}: {self.voter.username} -> {self.company.name}"


class VoteStatistics(models.Model):
    """投票统计表 - 用于缓存榜单排行"""
    category = models.CharField(max_length=50, db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    total_votes = models.IntegerField(default=0, verbose_name='总票数')
    vote_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0, verbose_name='得票率%')

    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    class Meta:
        db_table = 'vote_statistics'
        unique_together = ('category', 'company')
        verbose_name = '投票统计'
        verbose_name_plural = '投票统计'
        ordering = ['-vote_rate']


class Evidence(models.Model):
    """证据材料表 - 用户上传的截图/文档"""
    vote = models.ForeignKey(Vote, related_name='evidences', on_delete=models.CASCADE, verbose_name='关联投票')
    file_path = models.CharField(max_length=500, verbose_name='文件路径')
    file_type = models.CharField(max_length=20, choices=[('image', '图片'), ('document', '文档')], verbose_name='文件类型')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidence'
        verbose_name = '证据材料'
        verbose_name_plural = '证据材料'

    def __str__(self):
        return f"Evidence-{self.id}: {self.vote}"


# 全局变量存储待处理的上传任务
pending_uploads = {}
