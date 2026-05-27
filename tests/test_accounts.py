"""
accounts模块单元测试
运行方式: python manage.py test tests.test_accounts
"""
import json
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from accounts.models import User, DormBuilding, DormRoom
from accounts.views import login_view, logout_view, profile_view, building_list_view, room_list_view


class LoginTest(TestCase):
    """登录测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            account='testuser', username='testuser', password='test123456',
            name='测试用户', role='student', student_or_staff_no='T001', phone='13800000001'
        )

    def test_login_success(self):
        """测试登录成功"""
        request = self.factory.post('/api/accounts/login/',
            data=json.dumps({'account': 'testuser', 'password': 'test123456'}),
            content_type='application/json')
        response = login_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['account'], 'testuser')

    def test_login_wrong_password(self):
        """测试密码错误"""
        request = self.factory.post('/api/accounts/login/',
            data=json.dumps({'account': 'testuser', 'password': 'wrong'}),
            content_type='application/json')
        response = login_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '账号或密码错误')

    def test_login_nonexistent_account(self):
        """测试不存在的账号"""
        request = self.factory.post('/api/accounts/login/',
            data=json.dumps({'account': 'nouser', 'password': '123456'}),
            content_type='application/json')
        response = login_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], '账号不存在')

    def test_login_lockout(self):
        """测试登录锁定"""
        # 连续失败5次
        for i in range(5):
            request = self.factory.post('/api/accounts/login/',
                data=json.dumps({'account': 'testuser', 'password': 'wrong'}),
                content_type='application/json')
            login_view(request)

        # 第6次应该被锁定
        request = self.factory.post('/api/accounts/login/',
            data=json.dumps({'account': 'testuser', 'password': 'test123456'}),
            content_type='application/json')
        response = login_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('锁定', response.data['error'])


class ProfileTest(TestCase):
    """个人信息测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            account='testuser', username='testuser', password='test123456',
            name='测试用户', role='student', student_or_staff_no='T001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_get_profile(self):
        """测试获取个人信息"""
        request = self.factory.get('/api/accounts/profile/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.user
        response = profile_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['account'], 'testuser')

    def test_update_profile(self):
        """测试更新个人信息"""
        request = self.factory.put('/api/accounts/profile/',
            data=json.dumps({'name': '新名字', 'phone': '13900000001'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.user
        response = profile_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], '新名字')


class BuildingRoomTest(TestCase):
    """宿舍楼和房间测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            account='testuser', username='testuser', password='test123456',
            name='测试用户', role='student', student_or_staff_no='T001', phone='13800000001'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.building = DormBuilding.objects.create(
            building_code='T01', building_name='测试楼', gender_limit='男'
        )
        DormRoom.objects.create(building=self.building, room_no='101', floor_no=1)

    def test_get_buildings(self):
        """测试获取宿舍楼列表"""
        request = self.factory.get('/api/accounts/buildings/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.user
        response = building_list_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_rooms(self):
        """测试获取房间列表"""
        request = self.factory.get(f'/api/accounts/rooms/?building={self.building.id}',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        request.user = self.user
        response = room_list_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
