from django.db import models


class Evaluation(models.Model):
    """服务评价"""
    work_order = models.OneToOneField(
        'repairs.WorkOrder',
        on_delete=models.CASCADE,
        related_name='evaluation',
        verbose_name='对应工单'
    )
    speed_score = models.IntegerField('维修速度评分')  # 1-5
    attitude_score = models.IntegerField('服务态度评分')  # 1-5
    quality_score = models.IntegerField('维修质量评分')  # 1-5
    content = models.TextField('文字评价', max_length=500, blank=True, null=True)
    created_at = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        db_table = 'evaluation'
        verbose_name = '服务评价'
        verbose_name_plural = '服务评价'

    def __str__(self):
        return f'{self.work_order.order_no} - 评价'

    @property
    def avg_score(self):
        return round((self.speed_score + self.attitude_score + self.quality_score) / 3, 1)


class Complaint(models.Model):
    """投诉记录"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已处理'),
    ]
    TYPE_CHOICES = [
        ('quality', '维修质量'),
        ('attitude', '服务态度'),
        ('other', '其他'),
    ]

    work_order = models.ForeignKey(
        'repairs.WorkOrder',
        on_delete=models.CASCADE,
        related_name='complaints',
        verbose_name='对应工单'
    )
    student = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        verbose_name='投诉人'
    )
    type = models.CharField('投诉类型', max_length=20, choices=TYPE_CHOICES, default='quality')
    content = models.TextField('投诉内容', max_length=1000)
    process_result = models.TextField('处理结果', max_length=1000, blank=True, null=True)
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    handled_at = models.DateTimeField('处理时间', null=True, blank=True)

    class Meta:
        db_table = 'complaint'
        verbose_name = '投诉记录'
        verbose_name_plural = '投诉记录'

    def __str__(self):
        return f'{self.work_order.order_no} - 投诉'
