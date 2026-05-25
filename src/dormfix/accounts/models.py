from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = [
        ('student', '学生'),
        ('admin', '宿舍管理员'),
        ('maintainer', '维修人员'),
    ]

    account = models.CharField('登录账号', max_length=50, unique=True)
    name = models.CharField('姓名', max_length=50)
    student_or_staff_no = models.CharField('学号/工号', max_length=30, db_index=True)
    phone = models.CharField('联系电话', max_length=20)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES)
    status = models.SmallIntegerField('账号状态', default=1)  # 1=启用, 0=禁用
    login_attempts = models.IntegerField('登录失败次数', default=0)
    lockout_until = models.DateTimeField('锁定截止时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    USERNAME_FIELD = 'account'
    REQUIRED_FIELDS = ['name', 'role', 'student_or_staff_no']

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.name}({self.get_role_display()})'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_maintainer(self):
        return self.role == 'maintainer'


class DormBuilding(models.Model):
    """宿舍楼"""
    building_code = models.CharField('楼栋编号', max_length=20, unique=True)
    building_name = models.CharField('楼栋名称', max_length=50)
    gender_limit = models.CharField('性别限制', max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'dorm_building'
        verbose_name = '宿舍楼'
        verbose_name_plural = '宿舍楼'

    def __str__(self):
        return self.building_name


class DormRoom(models.Model):
    """宿舍房间"""
    building = models.ForeignKey(
        DormBuilding,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='所属楼栋'
    )
    room_no = models.CharField('房间号', max_length=20, db_index=True)
    floor_no = models.IntegerField('楼层')

    class Meta:
        db_table = 'dorm_room'
        unique_together = [('building', 'room_no')]
        verbose_name = '宿舍房间'
        verbose_name_plural = '宿舍房间'

    def __str__(self):
        return f'{self.building.building_name}-{self.room_no}'
