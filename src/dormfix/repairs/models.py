import time
import random

from django.db import models


class WorkOrder(models.Model):
    """报修工单"""
    CATEGORY_CHOICES = [
        ('water_electric', '水电'),
        ('door_window', '门窗'),
        ('network', '网络'),
        ('furniture', '家具'),
        ('other', '其他'),
    ]
    URGENCY_CHOICES = [
        ('normal', '普通'),
        ('urgent', '紧急'),
    ]
    STATUS_CHOICES = [
        ('pending_review', '待审核'),
        ('pending_dispatch', '待派单'),
        ('assigned', '已派单'),
        ('in_progress', '处理中'),
        ('pending_confirm', '已完成待确认'),
        ('completed', '已完成'),
        ('evaluated', '已评价'),
        ('rejected', '已驳回'),
        ('cancelled', '已撤销'),
    ]

    order_no = models.CharField('工单编号', max_length=40, unique=True)
    student = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='student_orders',
        verbose_name='报修学生'
    )
    maintainer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintainer_orders',
        verbose_name='维修人员'
    )
    room = models.ForeignKey(
        'accounts.DormRoom',
        on_delete=models.PROTECT,
        verbose_name='宿舍房间'
    )
    category = models.CharField('报修类别', max_length=30, choices=CATEGORY_CHOICES, db_index=True)
    description = models.TextField('故障描述', max_length=1000)
    urgency_level = models.CharField('紧急程度', max_length=10, choices=URGENCY_CHOICES, default='normal')
    status = models.CharField('工单状态', max_length=20, choices=STATUS_CHOICES, default='pending_review', db_index=True)
    submit_time = models.DateTimeField('提交时间', auto_now_add=True)
    assign_time = models.DateTimeField('派单时间', null=True, blank=True)
    finish_time = models.DateTimeField('完成时间', null=True, blank=True)
    cancel_flag = models.SmallIntegerField('是否撤销', default=0)

    class Meta:
        db_table = 'work_order'
        ordering = ['-submit_time']
        verbose_name = '报修工单'
        verbose_name_plural = '报修工单'

    def __str__(self):
        return f'{self.order_no} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f'WX{int(time.time())}{random.randint(1000, 9999)}'
        super().save(*args, **kwargs)

    @property
    def image_urls(self):
        return [img.image.url for img in self.images.all()]


class WorkOrderImage(models.Model):
    """工单图片"""
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='所属工单'
    )
    image = models.ImageField('图片', upload_to='repair_images/')

    class Meta:
        db_table = 'work_order_image'
        verbose_name = '工单图片'
        verbose_name_plural = '工单图片'


class WorkOrderLog(models.Model):
    """工单处理日志"""
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='所属工单'
    )
    operator = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        verbose_name='操作人'
    )
    from_status = models.CharField('原状态', max_length=20, blank=True, null=True)
    to_status = models.CharField('新状态', max_length=20)
    operation_type = models.CharField('操作类型', max_length=30)
    operation_time = models.DateTimeField('操作时间', auto_now_add=True)
    remark = models.TextField('备注说明', max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'work_order_log'
        ordering = ['operation_time']
        verbose_name = '工单日志'
        verbose_name_plural = '工单日志'

    def __str__(self):
        return f'{self.work_order.order_no} - {self.operation_type}'
