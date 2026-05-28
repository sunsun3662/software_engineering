from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rest_framework.pagination import PageNumberPagination

from .models import User, DormBuilding, DormRoom
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer, DormBuildingSerializer, DormRoomSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """用户登录"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    account = serializer.validated_data['account']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(account=account)
    except User.DoesNotExist:
        return Response({'error': '账号不存在'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查锁定状态
    if user.lockout_until and user.lockout_until > timezone.now():
        remaining = (user.lockout_until - timezone.now()).seconds // 60 + 1
        return Response(
            {'error': f'账户已临时锁定，请于{remaining}分钟后重试'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 验证密码
    user_auth = authenticate(account=account, password=password)

    if user_auth is None:
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.lockout_until = timezone.now() + timezone.timedelta(minutes=15)
            user.login_attempts = 0
            user.save()
            return Response(
                {'error': '账户已临时锁定，请于15分钟后重试'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.save()
        return Response({'error': '账号或密码错误'}, status=status.HTTP_400_BAD_REQUEST)

    if user.status == 0:
        return Response({'error': '账号已禁用'}, status=status.HTTP_400_BAD_REQUEST)

    # 登录成功，重置失败次数
    user.login_attempts = 0
    user.lockout_until = None
    user.save()

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'account': user.account,
            'name': user.name,
            'role': user.role,
            'student_or_staff_no': user.student_or_staff_no,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """用户登出"""
    request.user.auth_token.delete()
    return Response({'message': '登出成功'})


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """获取/更新个人信息"""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)

    # PUT 更新
    user = request.user
    if 'name' in request.data:
        user.name = request.data['name']
    if 'phone' in request.data:
        user.phone = request.data['phone']
    user.save()

    return Response({
        'id': user.id,
        'name': user.name,
        'phone': user.phone,
        'message': '更新成功'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def building_list_view(request):
    """宿舍楼列表"""
    buildings = DormBuilding.objects.all()
    serializer = DormBuildingSerializer(buildings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_list_view(request):
    """房间列表"""
    building_id = request.query_params.get('building')
    rooms = DormRoom.objects.all()
    if building_id:
        rooms = rooms.filter(building_id=building_id)
    serializer = DormRoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_list_create_view(request):
    """管理员：用户列表 / 创建用户"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        users = User.objects.all().order_by('-created_at')

        # 筛选
        role_filter = request.query_params.get('role')
        status_filter = request.query_params.get('status')
        if role_filter:
            users = users.filter(role=role_filter)
        if status_filter is not None:
            users = users.filter(status=int(status_filter))

        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # POST: 创建用户
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_detail_view(request, pk):
    """管理员：查看/修改用户"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserSerializer(user).data)

    # PUT: 修改用户（启用/禁用、修改角色等）
    if 'status' in request.data:
        user.status = int(request.data['status'])
    if 'role' in request.data:
        user.role = request.data['role']
    if 'name' in request.data:
        user.name = request.data['name']
    if 'phone' in request.data:
        user.phone = request.data['phone']
    if 'student_or_staff_no' in request.data:
        user.student_or_staff_no = request.data['student_or_staff_no']
    user.save()

    return Response(UserSerializer(user).data)
