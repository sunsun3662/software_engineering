from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from repairs.models import WorkOrder, WorkOrderLog
from repairs.serializers import WorkOrderListSerializer, WorkOrderDetailSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_list_view(request):
    """获取我的任务列表"""
    if not request.user.is_maintainer:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    orders = WorkOrder.objects.filter(maintainer=request.user)

    # 筛选
    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    else:
        # 默认显示进行中的任务
        orders = orders.filter(status__in=['assigned', 'in_progress', 'pending_confirm'])

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(orders, request)
    serializer = WorkOrderListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_task_view(request, pk):
    """接收任务 (UC007)"""
    if not request.user.is_maintainer:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk, maintainer=request.user)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'assigned':
        return Response({'error': '该工单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'in_progress'
    order.save()

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='assigned',
        to_status='in_progress',
        operation_type='接收任务'
    )

    return Response({'message': '已接单', 'status': 'in_progress'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task_view(request, pk):
    """完成维修 (UC008)"""
    if not request.user.is_maintainer:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk, maintainer=request.user)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'in_progress':
        return Response({'error': '该工单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

    result = request.data.get('result', '')
    materials = request.data.get('materials', '')

    if not result:
        return Response({'result': ['请填写维修结果']}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'pending_confirm'
    order.finish_time = timezone.now()
    order.save()

    remark = f'维修结果: {result}'
    if materials:
        remark += f'\n耗材: {materials}'

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='in_progress',
        to_status='pending_confirm',
        operation_type='完成维修',
        remark=remark
    )

    return Response({'message': '维修完成，等待学生确认', 'status': 'pending_confirm'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_task_view(request, pk):
    """学生确认完成 (UC009)"""
    if not request.user.is_student:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=pk, student=request.user)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 检查是否超过3天自动确认
    if order.status == 'pending_confirm' and order.finish_time:
        if timezone.now() - order.finish_time > timedelta(days=3):
            order.status = 'completed'
            order.save()
            WorkOrderLog.objects.create(
                work_order=order,
                operator=request.user,
                from_status='pending_confirm',
                to_status='completed',
                operation_type='系统自动确认'
            )

    if order.status != 'pending_confirm':
        return Response({'error': '该工单状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)

    confirmed = request.data.get('confirmed', True)

    if confirmed:
        order.status = 'completed'
        order.save()
        WorkOrderLog.objects.create(
            work_order=order,
            operator=request.user,
            from_status='pending_confirm',
            to_status='completed',
            operation_type='确认完成'
        )
        return Response({'message': '已确认完成', 'status': 'completed'})
    else:
        reason = request.data.get('reason', '')
        order.status = 'in_progress'
        order.save()
        WorkOrderLog.objects.create(
            work_order=order,
            operator=request.user,
            from_status='pending_confirm',
            to_status='in_progress',
            operation_type='申请返修',
            remark=reason
        )
        return Response({'message': '已申请返修', 'status': 'in_progress'})
