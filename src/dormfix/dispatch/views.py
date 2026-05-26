from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from repairs.models import WorkOrder, WorkOrderLog
from repairs.serializers import WorkOrderListSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_review_list_view(request):
    """获取待审核列表"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    orders = WorkOrder.objects.filter(status='pending_review')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(orders, request)
    serializer = WorkOrderListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_view(request, pk):
    """审核通过 (UC005)"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'pending_review':
        return Response({'error': '该工单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'pending_dispatch'
    order.save()

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='pending_review',
        to_status='pending_dispatch',
        operation_type='审核通过'
    )

    return Response({'message': '审核通过，工单已进入派单队列', 'status': 'pending_dispatch'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_view(request, pk):
    """审核驳回 (UC005)"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'pending_review':
        return Response({'error': '该工单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

    reason = request.data.get('reason', '')
    if not reason:
        return Response({'reason': ['请填写驳回理由']}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'rejected'
    order.save()

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='pending_review',
        to_status='rejected',
        operation_type='审核驳回',
        remark=reason
    )

    return Response({'message': '已驳回', 'status': 'rejected'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_dispatch_list_view(request):
    """获取待派单列表"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    orders = WorkOrder.objects.filter(status='pending_dispatch')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(orders, request)
    serializer = WorkOrderListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def maintainer_list_view(request):
    """获取维修人员列表"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    maintainers = User.objects.filter(role='maintainer', status=1)
    today = timezone.now().date()

    result = []
    for m in maintainers:
        today_count = WorkOrder.objects.filter(
            maintainer=m,
            assign_time__date=today
        ).count()
        result.append({
            'id': m.id,
            'name': m.name,
            'student_or_staff_no': m.student_or_staff_no,
            'phone': m.phone,
            'today_task_count': today_count,
            'status': '在岗'
        })

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_view(request, pk):
    """派发任务 (UC006)"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'pending_dispatch':
        return Response({'error': '该工单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

    maintainer_id = request.data.get('maintainer_id')
    if not maintainer_id:
        return Response({'maintainer_id': ['请选择维修人员']}, status=status.HTTP_400_BAD_REQUEST)

    try:
        maintainer = User.objects.get(id=maintainer_id, role='maintainer')
    except User.DoesNotExist:
        return Response({'error': '维修人员不存在'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查维修人员今日任务数
    today = timezone.now().date()
    today_count = WorkOrder.objects.filter(
        maintainer=maintainer,
        assign_time__date=today
    ).count()
    if today_count >= 5:
        return Response({'error': '该维修人员今日任务已饱和，请重新选择'}, status=status.HTTP_400_BAD_REQUEST)

    order.maintainer = maintainer
    order.status = 'assigned'
    order.assign_time = timezone.now()
    order.save()

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='pending_dispatch',
        to_status='assigned',
        operation_type='派发任务',
        remark=f'派给{maintainer.name}'
    )

    return Response({'message': '派发成功', 'status': 'assigned'})
