"""
种子数据脚本
运行方式: python create_seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dormfix.settings')
sys.stdout.reconfigure(encoding='utf-8')
django.setup()

from accounts.models import User, DormBuilding, DormRoom


def create_seed_data():
    print('开始创建种子数据...')

    # 创建管理员
    if not User.objects.filter(account='admin').exists():
        User.objects.create_superuser(
            account='admin', username='admin', password='admin123456',
            name='管理员', role='admin', student_or_staff_no='A001', phone='13800000000'
        )
        print('创建管理员: admin / admin123456')

    # 创建学生
    students = [
        ('student001', '张三', '2023001', '13800000001'),
        ('student002', '李四', '2023002', '13800000002'),
        ('student003', '王五', '2023003', '13800000003'),
    ]
    for account, name, no, phone in students:
        if not User.objects.filter(account=account).exists():
            User.objects.create_user(
                account=account, username=account, password='123456',
                name=name, role='student', student_or_staff_no=no, phone=phone
            )
            print(f'创建学生: {account} / 123456')

    # 创建维修人员
    maintainers = [
        ('maintainer001', '王师傅', 'W001', '13700000001'),
        ('maintainer002', '李师傅', 'W002', '13700000002'),
        ('maintainer003', '赵师傅', 'W003', '13700000003'),
    ]
    for account, name, no, phone in maintainers:
        if not User.objects.filter(account=account).exists():
            User.objects.create_user(
                account=account, username=account, password='123456',
                name=name, role='maintainer', student_or_staff_no=no, phone=phone
            )
            print(f'创建维修人员: {account} / 123456')

    # 创建宿舍楼
    buildings = [
        ('A01', '1号楼', '男'),
        ('A02', '2号楼', '女'),
        ('A03', '3号楼', '男'),
    ]
    for code, name, gender in buildings:
        if not DormBuilding.objects.filter(building_code=code).exists():
            DormBuilding.objects.create(building_code=code, building_name=name, gender_limit=gender)
            print(f'创建宿舍楼: {name}')

    # 创建房间
    building_objs = DormBuilding.objects.all()
    for building in building_objs:
        for floor in range(1, 6):  # 5层
            for room in range(1, 5):  # 每层4间
                room_no = f'{floor}0{room}'
                if not DormRoom.objects.filter(building=building, room_no=room_no).exists():
                    DormRoom.objects.create(building=building, room_no=room_no, floor_no=floor)

    print(f'创建房间: {DormRoom.objects.count()} 间')
    print('种子数据创建完成！')
    print()
    print('测试账号:')
    print('  管理员: admin / admin123456')
    print('  学生: student001 / 123456')
    print('  维修人员: maintainer001 / 123456')


if __name__ == '__main__':
    create_seed_data()
