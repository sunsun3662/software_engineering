from django.utils import timezone
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WorkOrder, WorkOrderLog
from .serializers import WorkOrderListSerializer, WorkOrderDetailSerializer, WorkOrderCreateSerializer


# 状态流转规则
VALID_TRANSITIONS = {
    'pending_review': ['pending_dispatch', 'rejected', 'cancelled'],
    'pending_dispatch': ['assigned'],
    'assigned': ['in_progress'],
    'in_progress': ['pending_confirm'],
    'pending_confirm': ['completed', 'in_progress'],
    'completed': ['evaluated'],
}


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list_create_view(request):
    """
    GET: 获取工单列表
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
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
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
        return Response({'error': '您当前有多个工单正在处理中，暂不能提交新报修'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = WorkOrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = serializer.save(student=request.user)

    return Response(WorkOrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)


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

    serializer = WorkOrderDetailSerializer(order)
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
