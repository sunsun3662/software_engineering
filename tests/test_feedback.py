"""
feedback模块单元测试
运行方式: python manage.py test tests.test_feedback
"""
import json
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from accounts.models import User, DormBuilding, DormRoom
from repairs.models import WorkOrder
from feedback.models import Evaluation, Complaint
from feedback.views import evaluate_view, complaint_create_view, complaint_list_view, complaint_process_view


class EvaluateTest(TestCase):
    """评价测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.student)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_evaluate_success(self):
        """测试评价成功"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='completed'
        )
        request = self.factory.post('/',
            data=json.dumps({'speed_score': 5, 'attitude_score': 4, 'quality_score': 5, 'content': '很好'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = evaluate_view(request, work_order_id=order.id)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Evaluation.objects.filter(work_order=order).exists())

    def test_evaluate_wrong_status(self):
        """测试非已完成状态不能评价"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='in_progress'
        )
        request = self.factory.post('/',
            data=json.dumps({'speed_score': 5, 'attitude_score': 4, 'quality_score': 5}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = evaluate_view(request, work_order_id=order.id)
        self.assertEqual(response.status_code, 400)

    def test_evaluate_duplicate(self):
        """测试不能重复评价"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='completed'
        )
        Evaluation.objects.create(
            work_order=order, speed_score=5, attitude_score=5, quality_score=5
        )
        request = self.factory.post('/',
            data=json.dumps({'speed_score': 5, 'attitude_score': 4, 'quality_score': 5}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = evaluate_view(request, work_order_id=order.id)
        self.assertEqual(response.status_code, 400)

    def test_evaluate_score_range(self):
        """测试评分范围"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='completed'
        )
        request = self.factory.post('/',
            data=json.dumps({'speed_score': 6, 'attitude_score': 4, 'quality_score': 5}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.student
        response = evaluate_view(request, work_order_id=order.id)
        self.assertEqual(response.status_code, 400)


class ComplaintTest(TestCase):
    """投诉测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.student = User.objects.create_user(
            account='student', username='student', password='123456',
            name='学生', role='student', student_or_staff_no='S001', phone='13800000001'
        )
        self.admin = User.objects.create_user(
            account='admin', username='admin', password='123456',
            name='管理员', role='admin', student_or_staff_no='A001', phone='13800000002'
        )
        self.student_token, _ = Token.objects.get_or_create(user=self.student)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.building = DormBuilding.objects.create(building_code='B01', building_name='1号楼')
        self.room = DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_complaint_success(self):
        """测试投诉成功"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='completed'
        )
        request = self.factory.post('/',
            data=json.dumps({'type': 'quality', 'content': '没修好'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        request.user = self.student
        response = complaint_create_view(request, work_order_id=order.id)
        self.assertEqual(response.status_code, 201)

    def test_complaint_duplicate(self):
        """测试不能重复投诉"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='completed'
        )
        Complaint.objects.create(
            work_order=order, student=self.student,
            type='quality', content='投诉内容'
        )
        request = self.factory.post('/',
            data=json.dumps({'type': 'quality', 'content': '再次投诉'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        request.user = self.student
        response = complaint_create_view(request, work_order_id=order.id)
        self.assertEqual(response.status_code, 400)

    def test_complaint_list(self):
        """测试投诉列表"""
        request = self.factory.get('/', HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = complaint_list_view(request)
        self.assertEqual(response.status_code, 200)

    def test_process_complaint(self):
        """测试处理投诉"""
        order = WorkOrder.objects.create(
            student=self.student, room=self.room,
            category='water_electric', description='测试',
            status='completed'
        )
        complaint = Complaint.objects.create(
            work_order=order, student=self.student,
            type='quality', content='投诉内容'
        )
        request = self.factory.post('/',
            data=json.dumps({'result': '已处理', 'status': 'resolved'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        request.user = self.admin
        response = complaint_process_view(request, pk=complaint.id)
        self.assertEqual(response.status_code, 200)
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'resolved')
