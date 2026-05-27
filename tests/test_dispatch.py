"""
dispatch模块单元测试
运行方式: python manage.py test tests.test_dispatch
"""
import json
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from accounts.models import User, DormBuilding, DormRoom
from repairs.models import WorkOrder
from dispatch.views import approve_view, reject_view, assign_view, maintainer_list_view


class ApproveTest(TestCase):
    """审核测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = User.objects.create_user(
            account='admin', username='admin', password='123456',
            name='管理员', role='admin', student_or_staff_no='A001', phone='13800000001'
        )
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000002'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_approve_success(self):
        """测试审核通过"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试'
        )
        request = self.factory.post('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = approve_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'pending_dispatch')

    def test_reject_success(self):
        """测试审核驳回"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试'
        )
        request = self.factory.post('/',
            data=json.dumps({'reason': '信息不全'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = reject_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'rejected')

    def test_reject_need_reason(self):
        """测试驳回需要理由"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试'
        )
        request = self.factory.post('/',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = reject_view(request, pk=order.id)
        self.assertEqual(response.status_code, 400)


class AssignTest(TestCase):
    """派单测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = User.objects.create_user(
            account='admin', username='admin', password='123456',
            name='管理员', role='admin', student_or_staff_no='A001', phone='13800000001'
        )
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000002'
        )
        self.maintainer = User.objects.create_user(
            account='maintainer', username='maintainer', password='123456',
            name='维修工', role='maintainer', student_or_staff_no='W001', phone='13800000003'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_assign_success(self):
        """测试派单成功"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试'
        )
        order.status = 'pending_dispatch'
        order.save()
        request = self.factory.post('/',
            data=json.dumps({'maintainer_id': self.maintainer.id}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = assign_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'assigned')
        self.assertEqual(order.maintainer, self.maintainer)

    def test_assign_limit(self):
        """测试维修人员任务上限"""
        from django.utils import timezone
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试'
        )
        order.status = 'pending_dispatch'
        order.save()

        # 创建5个今日任务
        for i in range(5):
            o = WorkOrder.objects.create(
                student=self.student, room=self.room,
                category='other', description=f'历史{i}'
            )
            o.maintainer = self.maintainer
            o.assign_time = timezone.now()
            o.save()

        request = self.factory.post('/',
            data=json.dumps({'maintainer_id': self.maintainer.id}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = assign_view(request, pk=order.id)
        self.assertEqual(response.status_code, 400)

    def test_get_maintainers(self):
        """测试获取维修人员列表"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = maintainer_list_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
