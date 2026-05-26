from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WorkOrder, WorkOrderLog, WorkOrderImage
from .serializers import WorkOrderListSerializer, WorkOrderDetailSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list_create_view(request):
    """
    GET: 获取工单列表 (UC003)
    POST: 创建报修 (UC002)
    """
    if request.method == 'GET':
        user = request.user
        if user.is_student:
            orders = WorkOrder.objects.filter(student=user)
        else:
            orders = WorkOrder.objects.all()

        # 筛选
        status_filter = request.query_params.get('status')
        category_filter = request.query_params.get('category')
        if status_filter:
            orders = orders.filter(status=status_filter)
        if category_filter:
            orders = orders.filter(category=category_filter)

        # 分页
        paginator = PageNumberPagination()
        page_size = request.query_params.get('page_size')
        if page_size:
            paginator.page_size = int(page_size)
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(orders, request)
        serializer = WorkOrderListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # POST: 创建报修
    if not request.user.is_student:
        return Response({'error': '只有学生可以提交报修'}, status=status.HTTP_403_FORBIDDEN)

    # 检查未完成工单数
    pending_count = WorkOrder.objects.filter(
        student=request.user,
        status__in=['pending_review', 'pending_dispatch', 'assigned', 'in_progress', 'pending_confirm']
    ).count()
    if pending_count >= 3:
        return Response({'error': '您当前有多个工单正在处理中，暂不能提交新报修'}, status=status.HTTP_403_FORBIDDEN)

    # 获取参数
    room_id = request.data.get('room')
    category = request.data.get('category')
    description = request.data.get('description')
    urgency_level = request.data.get('urgency_level', 'normal')

    if not room_id or not category or not description:
        errors = {}
        if not room_id:
            errors['room'] = ['此字段不能为空']
        if not category:
            errors['category'] = ['此字段不能为空']
        if not description:
            errors['description'] = ['此字段不能为空']
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # 验证房间存在
    from accounts.models import DormRoom
    try:
        room = DormRoom.objects.get(id=room_id)
    except DormRoom.DoesNotExist:
        return Response({'room': ['房间不存在']}, status=status.HTTP_400_BAD_REQUEST)

    # 创建工单
    order = WorkOrder.objects.create(
        student=request.user,
        room=room,
        category=category,
        description=description,
        urgency_level=urgency_level
    )

    # 处理多图片上传
    images = request.FILES.getlist('images')
    if len(images) > 3:
        return Response({'images': ['最多上传3张图片']}, status=status.HTTP_400_BAD_REQUEST)
    for img in images:
        if img.size > 5 * 1024 * 1024:  # 5MB
            return Response({'images': ['图片大小不能超过5MB']}, status=status.HTTP_400_BAD_REQUEST)
        WorkOrderImage.objects.create(work_order=order, image=img)

    # 记录日志
    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        to_status='pending_review',
        operation_type='提交报修'
    )

    return Response(WorkOrderDetailSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail_view(request, pk):
    """获取工单详情 (UC003)"""
    try:
        order = WorkOrder.objects.get(pk=pk)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 权限检查：学生只能看自己的
    if request.user.is_student and order.student != request.user:
        return Response({'error': '无权查看'}, status=status.HTTP_403_FORBIDDEN)

    serializer = WorkOrderDetailSerializer(order, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_cancel_view(request, pk):
    """撤销工单 (UC004)"""
    if not request.user.is_student:
        return Response({'error': '只有学生可以撤销工单'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk, student=request.user)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'pending_review':
        return Response({'error': '该工单已被审核，无法撤销'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'cancelled'
    order.cancel_flag = 1
    order.save()

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='pending_review',
        to_status='cancelled',
        operation_type='撤销工单'
    )

    return Response({'message': '报修申请已撤销'})
