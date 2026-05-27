"""
maintenance模块单元测试
运行方式: python manage.py test tests.test_maintenance
"""
import json
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from accounts.models import User, DormBuilding, DormRoom
from repairs.models import WorkOrder
from maintenance.views import accept_task_view, complete_task_view, confirm_task_view


class AcceptTaskTest(TestCase):
    """接收任务测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.maintainer = User.objects.create_user(
            account='maintainer', username='maintainer', password='123456',
            name='维修工', role='maintainer', student_or_staff_no='W001', phone='13800000001'
        )
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000002'
        )
        self.token, _ = Token.objects.get_or_create(user=self.maintainer)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_accept_success(self):
        """测试接收任务成功"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            maintainer=self.maintainer, status='assigned'
        )
        request = self.factory.post('/', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.maintainer
        response = accept_task_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'in_progress')

    def test_cannot_accept_wrong_status(self):
        """测试不能接收非已派单状态的工单"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='pending_review'
        )
        request = self.factory.post('/', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.maintainer
        response = accept_task_view(request, pk=order.id)
        self.assertEqual(response.status_code, 404)  # 没有maintainer筛选


class CompleteTaskTest(TestCase):
    """完成维修测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.maintainer = User.objects.create_user(
            account='maintainer', username='maintainer', password='123456',
            name='维修工', role='maintainer', student_or_staff_no='W001', phone='13800000001'
        )
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000002'
        )
        self.token, _ = Token.objects.get_or_create(user=self.maintainer)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_complete_success(self):
        """测试完成维修成功"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            maintainer=self.maintainer, status='in_progress'
        )
        request = self.factory.post('/',
            data=json.dumps({'result': '已修好', 'materials': '新零件'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.maintainer
        response = complete_task_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'pending_confirm')

    def test_complete_need_result(self):
        """测试完成维修需要填写结果"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            maintainer=self.maintainer, status='in_progress'
        )
        request = self.factory.post('/',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.maintainer
        response = complete_task_view(request, pk=order.id)
        self.assertEqual(response.status_code, 400)


class ConfirmTaskTest(TestCase):
    """确认完成测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.maintainer = User.objects.create_user(
            account='maintainer', username='maintainer', password='123456',
            name='维修工', role='maintainer', student_or_staff_no='W001', phone='13800000002'
        )
        self.token, _ = Token.objects.get_or_create(user=self.student)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_confirm_success(self):
        """测试确认完成"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            maintainer=self.maintainer, status='pending_confirm'
        )
        request = self.factory.post('/',
            data=json.dumps({'confirmed': True}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = confirm_task_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'completed')

    def test_rework(self):
        """测试申请返修"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            maintainer=self.maintainer, status='pending_confirm'
        )
        request = self.factory.post('/',
            data=json.dumps({'confirmed': False, 'reason': '没修好'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = confirm_task_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'in_progress')
