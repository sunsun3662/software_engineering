"""
种子数据脚本
运行方式: python create_seed_data.py
"""
import os
import sys
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dormfix.settings')
sys.stdout.reconfigure(encoding='utf-8')
django.setup()

from django.utils import timezone
from accounts.models import User, DormBuilding, DormRoom
from repairs.models import WorkOrder, WorkOrderLog
from feedback.models import Evaluation, Complaint


def create_seed_data():
    print('开始创建种子数据...')

    # ========== 1. 创建用户 ==========
    # 创建管理员
    if not User.objects.filter(account='admin').exists():
        User.objects.create_superuser(
            account='admin', username='admin', password='admin123456',
            name='管理员', role='admin', student_or_staff_no='A001', phone='13800000000'
        )
        print('创建管理员: admin / admin123456')

    # 创建学生（20人）
    students = [
        ('student001', '张三', '2023001', '13800000001'),
        ('student002', '李四', '2023002', '13800000002'),
        ('student003', '王五', '2023003', '13800000003'),
        ('student004', '赵六', '2023004', '13800000004'),
        ('student005', '孙七', '2023005', '13800000005'),
        ('student006', '周八', '2023006', '13800000006'),
        ('student007', '吴九', '2023007', '13800000007'),
        ('student008', '郑十', '2023008', '13800000008'),
        ('student009', '刘洋', '2023009', '13800000009'),
        ('student010', '陈静', '2023010', '13800000010'),
        ('student011', '杨磊', '2024001', '13800000011'),
        ('student012', '黄丽', '2024002', '13800000012'),
        ('student013', '朱伟', '2024003', '13800000013'),
        ('student014', '马芳', '2024004', '13800000014'),
        ('student015', '胡强', '2024005', '13800000015'),
        ('student016', '郭敏', '2024006', '13800000016'),
        ('student017', '何涛', '2024007', '13800000017'),
        ('student018', '高雪', '2024008', '13800000018'),
        ('student019', '林峰', '2024009', '13800000019'),
        ('student020', '罗婷', '2024010', '13800000020'),
    ]
    for account, name, no, phone in students:
        if not User.objects.filter(account=account).exists():
            User.objects.create_user(
                account=account, username=account, password='123456',
                name=name, role='student', student_or_staff_no=no, phone=phone
            )
            print(f'创建学生: {account} / 123456')

    # 创建维修人员（5人）
    maintainers = [
        ('maintainer001', '王师傅', 'W001', '13700000001'),
        ('maintainer002', '李师傅', 'W002', '13700000002'),
        ('maintainer003', '赵师傅', 'W003', '13700000003'),
        ('maintainer004', '张师傅', 'W004', '13700000004'),
        ('maintainer005', '刘师傅', 'W005', '13700000005'),
    ]
    for account, name, no, phone in maintainers:
        if not User.objects.filter(account=account).exists():
            User.objects.create_user(
                account=account, username=account, password='123456',
                name=name, role='maintainer', student_or_staff_no=no, phone=phone
            )
            print(f'创建维修人员: {account} / 123456')

    # ========== 2. 创建宿舍楼和房间 ==========
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

    # ========== 3. 创建工单数据 ==========
    if WorkOrder.objects.count() == 0:
        print('开始创建工单数据...')

        # 获取用户和房间
        student1 = User.objects.get(account='student001')
        student2 = User.objects.get(account='student002')
        student3 = User.objects.get(account='student003')
        admin = User.objects.get(account='admin')
        maintainer1 = User.objects.get(account='maintainer001')
        maintainer2 = User.objects.get(account='maintainer002')

        room1 = DormRoom.objects.filter(building__building_code='A01').first()
        room2 = DormRoom.objects.filter(building__building_code='A01', room_no='102').first()
        room3 = DormRoom.objects.filter(building__building_code='A02').first()
        room4 = DormRoom.objects.filter(building__building_code='A03').first()

        now = timezone.now()

        # 工单1: 待审核 (student001)
        order1 = WorkOrder.objects.create(
            order_no='WX20260501001',
            student=student1,
            room=room1,
            category='water_electric',
            description='水龙头漏水，已经三天了，滴水很厉害',
            urgency_level='normal',
            status='pending_review',
            submit_time=now - timedelta(hours=2)
        )
        WorkOrderLog.objects.create(
            work_order=order1, operator=student1,
            to_status='pending_review', operation_type='提交报修'
        )

        # 工单2: 待派单 (student001) - 审核通过
        order2 = WorkOrder.objects.create(
            order_no='WX20260501002',
            student=student1,
            room=room1,
            category='door_window',
            description='宿舍门锁坏了，关不上门',
            urgency_level='urgent',
            status='pending_dispatch',
            submit_time=now - timedelta(days=1)
        )
        WorkOrderLog.objects.create(
            work_order=order2, operator=student1,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=1)
        )
        WorkOrderLog.objects.create(
            work_order=order2, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(hours=20),
            remark='紧急工单，优先处理'
        )
        order2.submit_time = now - timedelta(days=1)
        order2.save()

        # 工单3: 已派单 (student002)
        order3 = WorkOrder.objects.create(
            order_no='WX20260501003',
            student=student2,
            room=room2,
            category='network',
            description='宿舍网络无法连接，无法上网课',
            urgency_level='normal',
            status='assigned',
            submit_time=now - timedelta(days=2),
            assign_time=now - timedelta(hours=6)
        )
        order3.maintainer = maintainer1
        order3.save()
        WorkOrderLog.objects.create(
            work_order=order3, operator=student2,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=2)
        )
        WorkOrderLog.objects.create(
            work_order=order3, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(days=1, hours=12)
        )
        WorkOrderLog.objects.create(
            work_order=order3, operator=admin,
            from_status='pending_dispatch', to_status='assigned',
            operation_type='派发任务', remark='派给王师傅',
            operation_time=now - timedelta(hours=6)
        )

        # 工单4: 处理中 (student002)
        order4 = WorkOrder.objects.create(
            order_no='WX20260501004',
            student=student2,
            room=room2,
            category='furniture',
            description='书桌椅子坏了，坐着摇晃',
            urgency_level='normal',
            status='in_progress',
            submit_time=now - timedelta(days=3),
            assign_time=now - timedelta(days=1)
        )
        order4.maintainer = maintainer2
        order4.save()
        WorkOrderLog.objects.create(
            work_order=order4, operator=student2,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=3)
        )
        WorkOrderLog.objects.create(
            work_order=order4, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(days=2)
        )
        WorkOrderLog.objects.create(
            work_order=order4, operator=admin,
            from_status='pending_dispatch', to_status='assigned',
            operation_type='派发任务', remark='派给李师傅',
            operation_time=now - timedelta(days=1)
        )
        WorkOrderLog.objects.create(
            work_order=order4, operator=maintainer2,
            from_status='assigned', to_status='in_progress',
            operation_type='接收任务', operation_time=now - timedelta(hours=18)
        )

        # 工单5: 已完成待确认 (student003)
        order5 = WorkOrder.objects.create(
            order_no='WX20260501005',
            student=student3,
            room=room3,
            category='water_electric',
            description='宿舍灯泡坏了，需要更换',
            urgency_level='normal',
            status='pending_confirm',
            submit_time=now - timedelta(days=5),
            assign_time=now - timedelta(days=3),
            finish_time=now - timedelta(hours=3)
        )
        order5.maintainer = maintainer1
        order5.save()
        WorkOrderLog.objects.create(
            work_order=order5, operator=student3,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=5)
        )
        WorkOrderLog.objects.create(
            work_order=order5, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(days=4)
        )
        WorkOrderLog.objects.create(
            work_order=order5, operator=admin,
            from_status='pending_dispatch', to_status='assigned',
            operation_type='派发任务', operation_time=now - timedelta(days=3)
        )
        WorkOrderLog.objects.create(
            work_order=order5, operator=maintainer1,
            from_status='assigned', to_status='in_progress',
            operation_type='接收任务', operation_time=now - timedelta(days=2)
        )
        WorkOrderLog.objects.create(
            work_order=order5, operator=maintainer1,
            from_status='in_progress', to_status='pending_confirm',
            operation_type='完成维修', remark='已更换新灯泡',
            operation_time=now - timedelta(hours=3)
        )

        # 工单6: 已完成 (student001) - 可以评价
        order6 = WorkOrder.objects.create(
            order_no='WX20260501006',
            student=student1,
            room=room1,
            category='other',
            description='窗户玻璃有裂痕，存在安全隐患',
            urgency_level='normal',
            status='completed',
            submit_time=now - timedelta(days=10),
            assign_time=now - timedelta(days=8),
            finish_time=now - timedelta(days=6)
        )
        order6.maintainer = maintainer1
        order6.save()
        WorkOrderLog.objects.create(
            work_order=order6, operator=student1,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=10)
        )
        WorkOrderLog.objects.create(
            work_order=order6, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(days=9)
        )
        WorkOrderLog.objects.create(
            work_order=order6, operator=admin,
            from_status='pending_dispatch', to_status='assigned',
            operation_type='派发任务', operation_time=now - timedelta(days=8)
        )
        WorkOrderLog.objects.create(
            work_order=order6, operator=maintainer1,
            from_status='assigned', to_status='in_progress',
            operation_type='接收任务', operation_time=now - timedelta(days=7)
        )
        WorkOrderLog.objects.create(
            work_order=order6, operator=maintainer1,
            from_status='in_progress', to_status='pending_confirm',
            operation_type='完成维修', remark='已更换玻璃',
            operation_time=now - timedelta(days=6, hours=6)
        )
        WorkOrderLog.objects.create(
            work_order=order6, operator=student1,
            from_status='pending_confirm', to_status='completed',
            operation_type='确认完成', operation_time=now - timedelta(days=6)
        )

        # 工单7: 已评价 (student002)
        order7 = WorkOrder.objects.create(
            order_no='WX20260501007',
            student=student2,
            room=room2,
            category='water_electric',
            description='卫生间水箱漏水',
            urgency_level='normal',
            status='evaluated',
            submit_time=now - timedelta(days=15),
            assign_time=now - timedelta(days=13),
            finish_time=now - timedelta(days=11)
        )
        order7.maintainer = maintainer2
        order7.save()
        WorkOrderLog.objects.create(
            work_order=order7, operator=student2,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=15)
        )
        WorkOrderLog.objects.create(
            work_order=order7, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(days=14)
        )
        WorkOrderLog.objects.create(
            work_order=order7, operator=admin,
            from_status='pending_dispatch', to_status='assigned',
            operation_type='派发任务', operation_time=now - timedelta(days=13)
        )
        WorkOrderLog.objects.create(
            work_order=order7, operator=maintainer2,
            from_status='assigned', to_status='in_progress',
            operation_type='接收任务', operation_time=now - timedelta(days=12)
        )
        WorkOrderLog.objects.create(
            work_order=order7, operator=maintainer2,
            from_status='in_progress', to_status='pending_confirm',
            operation_type='完成维修', operation_time=now - timedelta(days=11, hours=12)
        )
        WorkOrderLog.objects.create(
            work_order=order7, operator=student2,
            from_status='pending_confirm', to_status='completed',
            operation_type='确认完成', operation_time=now - timedelta(days=11)
        )

        # 创建评价
        Evaluation.objects.create(
            work_order=order7,
            speed_score=5,
            attitude_score=4,
            quality_score=5,
            content='维修很及时，师傅态度很好，问题完全解决了'
        )
        order7.status = 'evaluated'
        order7.save()
        WorkOrderLog.objects.create(
            work_order=order7, operator=student2,
            from_status='completed', to_status='evaluated',
            operation_type='提交评价', operation_time=now - timedelta(days=10)
        )

        # 工单8: 已驳回 (student003)
        order8 = WorkOrder.objects.create(
            order_no='WX20260501008',
            student=student3,
            room=room3,
            category='other',
            description='想换新空调',
            urgency_level='normal',
            status='rejected',
            submit_time=now - timedelta(days=4)
        )
        WorkOrderLog.objects.create(
            work_order=order8, operator=student3,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=4)
        )
        WorkOrderLog.objects.create(
            work_order=order8, operator=admin,
            from_status='pending_review', to_status='rejected',
            operation_type='审核驳回', remark='非维修范围，属于设备更新需求',
            operation_time=now - timedelta(days=3)
        )

        # 工单9: 已撤销 (student001)
        order9 = WorkOrder.objects.create(
            order_no='WX20260501009',
            student=student1,
            room=room1,
            category='network',
            description='网速慢',
            urgency_level='normal',
            status='cancelled',
            cancel_flag=1,
            submit_time=now - timedelta(days=2)
        )
        WorkOrderLog.objects.create(
            work_order=order9, operator=student1,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=2)
        )
        WorkOrderLog.objects.create(
            work_order=order9, operator=student1,
            from_status='pending_review', to_status='cancelled',
            operation_type='撤销工单', remark='网络已自行恢复',
            operation_time=now - timedelta(days=1, hours=18)
        )

        # 工单10: 已完成待确认 - 有投诉 (student003)
        order10 = WorkOrder.objects.create(
            order_no='WX20260501010',
            student=student3,
            room=room3,
            category='door_window',
            description='阳台门关不严，漏风',
            urgency_level='normal',
            status='pending_confirm',
            submit_time=now - timedelta(days=7),
            assign_time=now - timedelta(days=5),
            finish_time=now - timedelta(days=2)
        )
        order10.maintainer = maintainer1
        order10.save()
        WorkOrderLog.objects.create(
            work_order=order10, operator=student3,
            to_status='pending_review', operation_type='提交报修',
            operation_time=now - timedelta(days=7)
        )
        WorkOrderLog.objects.create(
            work_order=order10, operator=admin,
            from_status='pending_review', to_status='pending_dispatch',
            operation_type='审核通过', operation_time=now - timedelta(days=6)
        )
        WorkOrderLog.objects.create(
            work_order=order10, operator=admin,
            from_status='pending_dispatch', to_status='assigned',
            operation_type='派发任务', operation_time=now - timedelta(days=5)
        )
        WorkOrderLog.objects.create(
            work_order=order10, operator=maintainer1,
            from_status='assigned', to_status='in_progress',
            operation_type='接收任务', operation_time=now - timedelta(days=4)
        )
        WorkOrderLog.objects.create(
            work_order=order10, operator=maintainer1,
            from_status='in_progress', to_status='pending_confirm',
            operation_type='完成维修', operation_time=now - timedelta(days=2)
        )

        # 创建投诉
        Complaint.objects.create(
            work_order=order10,
            student=student3,
            type='quality',
            content='维修后门还是关不严，感觉没修好',
            status='pending'
        )

        print(f'创建工单: {WorkOrder.objects.count()} 个')
        print(f'创建工单日志: {WorkOrderLog.objects.count()} 条')
        print(f'创建评价: {Evaluation.objects.count()} 条')
        print(f'创建投诉: {Complaint.objects.count()} 条')

    print()
    print('=' * 50)
    print('种子数据创建完成！')
    print('=' * 50)
    print()
    print('测试账号:')
    print('  管理员: admin / admin123456')
    print('  学生: student001 / 123456 (有多个工单)')
    print('  学生: student002 / 123456 (有工单和评价)')
    print('  学生: student003 / 123456 (有工单和投诉)')
    print('  维修人员: maintainer001 / 123456')
    print('  维修人员: maintainer002 / 123456')
    print()
    print('工单状态分布:')
    print('  - 待审核: 1个')
    print('  - 待派单: 1个')
    print('  - 已派单: 1个')
    print('  - 处理中: 1个')
    print('  - 已完成待确认: 2个')
    print('  - 已完成: 1个 (可评价)')
    print('  - 已评价: 1个')
    print('  - 已驳回: 1个')
    print('  - 已撤销: 1个')


if __name__ == '__main__':
    create_seed_data()
