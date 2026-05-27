"""
repairs模块单元测试
运行方式: python manage.py test tests.test_repairs
"""
import json
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from accounts.models import User, DormBuilding, DormRoom
from repairs.models import WorkOrder
from repairs.views import order_list_create_view, order_detail_view, order_cancel_view


class OrderCreateTest(TestCase):
    """创建报修测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.student)
        self.building = DormBuilding.objects.create(
            building_code='B01', building_name='1号楼'
        )
        self.room = DormRoom.objects.create(
            building=self.building, room_no='101', floor_no=1
        )

    def test_create_order_success(self):
        """测试创建报修成功"""
        request = self.factory.post('/api/repairs/',
            data={'room': self.room.id, 'category': 'water_electric', 'description': '水龙头漏水'},
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_list_create_view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending_review')

    def test_create_order_missing_field(self):
        """测试缺少必填字段"""
        request = self.factory.post('/api/repairs/',
            data={'room': self.room.id, 'category': 'water_electric'},
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_list_create_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('description', response.data)

    def test_create_order_limit(self):
        """测试未完成工单超限"""
        # 创建3个未完成工单
        for i in range(3):
            WorkOrder.objects.create(
                student=self.student, room=self.room,
                category='other', description=f'测试{i}'
            )

        # 第4个应该失败
        request = self.factory.post('/api/repairs/',
            data={'room': self.room.id, 'category': 'water_electric', 'description': '超限'},
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_list_create_view(request)
        self.assertEqual(response.status_code, 403)

    def test_non_student_cannot_create(self):
        """测试非学生不能创建报修"""
        admin = User.objects.create_user(
            account='admin', username='admin', password='123456',
            name='管理员', role='admin', student_or_staff_no='A001', phone='13800000002'
        )
        admin_token, _ = Token.objects.get_or_create(user=admin)
        request = self.factory.post('/api/repairs/',
            data={'room': self.room.id, 'category': 'water_electric', 'description': '测试'},
            HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        request.user = admin
        response = order_list_create_view(request)
        self.assertEqual(response.status_code, 403)


class OrderListTest(TestCase):
    """工单列表测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.student)
        self.building = DormBuilding.objects.create(
            building_code='B01', building_name='1号楼'
        )
        self.room = DormRoom.objects.create(
            building=self.building, room_no='101', floor_no=1
        )
        # 创建测试工单
        WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试工单'
        )

    def test_get_order_list(self):
        """测试获取工单列表"""
        request = self.factory.get('/api/repairs/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_list_create_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_student_only_see_own_orders(self):
        """测试学生只能看到自己的工单"""
        other_student = User.objects.create_user(
            account='other', username='other', password='123456',
            name='其他学生', role='student', student_or_staff_no='S002', phone='13800000002'
        )
        other_token, _ = Token.objects.get_or_create(user=other_student)
        request = self.factory.get('/api/repairs/',
            HTTP_AUTHORIZATION=f'Token {other_token.key}')
        request.user = other_student
        response = order_list_create_view(request)
        self.assertEqual(response.data['count'], 0)


class OrderDetailTest(TestCase):
    """工单详情测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.student)
        self.building = DormBuilding.objects.create(
            building_code='B01', building_name='1号楼'
        )
        self.room = DormRoom.objects.create(
            building=self.building, room_no='101', floor_no=1
        )
        self.order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试工单'
        )

    def test_get_order_detail(self):
        """测试获取工单详情"""
        request = self.factory.get(f'/api/repairs/{self.order.id}/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_detail_view(request, pk=self.order.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['order_no'], self.order.order_no)

    def test_cannot_see_others_order(self):
        """测试不能查看他人工单"""
        other_student = User.objects.create_user(
            account='other', username='other', password='123456',
            name='其他学生', role='student', student_or_staff_no='S002', phone='13800000002'
        )
        other_token, _ = Token.objects.get_or_create(user=other_student)
        request = self.factory.get(f'/api/repairs/{self.order.id}/',
            HTTP_AUTHORIZATION=f'Token {other_token.key}')
        request.user = other_student
        response = order_detail_view(request, pk=self.order.id)
        self.assertEqual(response.status_code, 403)


class OrderCancelTest(TestCase):
    """撤销工单测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.student)
        self.building = DormBuilding.objects.create(
            building_code='B01', building_name='1号楼'
        )
        self.room = DormRoom.objects.create(
            building=self.building, room_no='101', floor_no=1
        )

    def test_cancel_pending_order(self):
        """测试撤销待审核工单"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='待撤销'
        )
        request = self.factory.post(f'/api/repairs/{order.id}/cancel/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_cancel_view(request, pk=order.id)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

    def test_cannot_cancel_approved_order(self):
        """测试不能撤销已审核工单"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='已审核'
        )
        order.status = 'pending_dispatch'
        order.save()
        request = self.factory.post(f'/api/repairs/{order.id}/cancel/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = order_cancel_view(request, pk=order.id)
        self.assertEqual(response.status_code, 400)
