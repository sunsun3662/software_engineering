"""
dashboard模块单元测试
运行方式: python manage.py test tests.test_dashboard
"""
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from accounts.models import User, DormBuilding, DormRoom
from repairs.models import WorkOrder
from feedback.models import Evaluation
from dashboard.views import statistics_view, export_view


class StatisticsTest(TestCase):
    """统计测试"""

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

        # 创建测试数据
        for i in range(5):
            order = WorkOrder.objects.create(
                student=self.student, room=self.room,
                category='water_electric', description=f'测试{i}'
            )
            if i < 3:
                order.status = 'completed'
                order.maintainer = self.maintainer
                order.save()
                Evaluation.objects.create(
                    work_order=order, speed_score=5, attitude_score=4, quality_score=5
                )

    def test_statistics_success(self):
        """测试统计成功"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['summary']['total_orders'], 5)
        self.assertEqual(response.data['summary']['completed_orders'], 3)
        self.assertEqual(response.data['summary']['completion_rate'], 60.0)

    def test_statistics_with_filter(self):
        """测试带筛选条件的统计"""
        request = self.factory.get('/?category=water_electric',
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)

    def test_statistics_permission(self):
        """测试权限控制"""
        student_token, _ = Token.objects.get_or_create(user=self.student)
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {student_token.key}')
        request.user = self.student
        response = statistics_view(request)
        self.assertEqual(response.status_code, 403)

    def test_category_distribution(self):
        """测试类别分布"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['category_distribution']), 1)

    def test_status_distribution(self):
        """测试状态分布"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['status_distribution']) > 0)

    def test_daily_trend(self):
        """测试每日趋势"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['daily_trend']), 7)

    def test_maintainer_performance(self):
        """测试维修人员绩效"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['maintainer_performance']), 1)

    def test_satisfaction_distribution(self):
        """测试满意度分布"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = statistics_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['satisfaction_distribution']) > 0)


class ExportTest(TestCase):
    """导出测试"""

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
        WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试'
        )

    def test_export_success(self):
        """测试导出成功"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = export_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_export_permission(self):
        """测试导出权限"""
        student_token, _ = Token.objects.get_or_create(user=self.student)
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {student_token.key}')
        request.user = self.student
        response = export_view(request)
        self.assertEqual(response.status_code, 403)
