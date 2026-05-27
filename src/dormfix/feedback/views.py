from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from repairs.models import WorkOrder, WorkOrderLog
from .models import Evaluation, Complaint


# 敏感词列表（简化版）
SENSITIVE_WORDS = ['垃圾', '废物', '骗子']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_view(request, work_order_id):
    """提交评价 (UC010)"""
    if not request.user.is_student:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=work_order_id, student=request.user)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'completed':
        return Response({'error': '该工单状态不允许评价'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查是否已评价
    if Evaluation.objects.filter(work_order=order).exists():
        return Response({'error': '该工单已评价'}, status=status.HTTP_400_BAD_REQUEST)

    speed_score = request.data.get('speed_score')
    attitude_score = request.data.get('attitude_score')
    quality_score = request.data.get('quality_score')
    content = request.data.get('content', '')

    # 验证评分
    errors = {}
    if not speed_score or not (1 <= int(speed_score) <= 5):
        errors['speed_score'] = ['评分范围为1-5']
    if not attitude_score or not (1 <= int(attitude_score) <= 5):
        errors['attitude_score'] = ['评分范围为1-5']
    if not quality_score or not (1 <= int(quality_score) <= 5):
        errors['quality_score'] = ['评分范围为1-5']
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # 敏感词检查
    if content:
        for word in SENSITIVE_WORDS:
            if word in content:
                return Response({'content': ['内容包含不当词汇，请修改']}, status=status.HTTP_400_BAD_REQUEST)

    evaluation = Evaluation.objects.create(
        work_order=order,
        speed_score=int(speed_score),
        attitude_score=int(attitude_score),
        quality_score=int(quality_score),
        content=content
    )

    order.status = 'evaluated'
    order.save()

    WorkOrderLog.objects.create(
        work_order=order,
        operator=request.user,
        from_status='completed',
        to_status='evaluated',
        operation_type='提交评价'
    )

    return Response({'message': '感谢您的评价', 'evaluation_id': evaluation.id}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complaint_create_view(request, work_order_id):
    """提交投诉 (UC011)"""
    if not request.user.is_student:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = WorkOrder.objects.get(pk=work_order_id, student=request.user)
    except WorkOrder.DoesNotExist:
        return Response({'error': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)

    if order.status not in ['completed', 'evaluated']:
        return Response({'error': '该工单状态不允许投诉'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查是否已有处理中的投诉
    if Complaint.objects.filter(work_order=order, status__in=['pending', 'processing']).exists():
        return Response({'error': '该工单已有投诉在处理中，请勿重复提交'}, status=status.HTTP_400_BAD_REQUEST)

    complaint_type = request.data.get('type', 'quality')
    content = request.data.get('content', '')

    if not content:
        return Response({'content': ['请填写投诉内容']}, status=status.HTTP_400_BAD_REQUEST)

    complaint = Complaint.objects.create(
        work_order=order,
        student=request.user,
        type=complaint_type,
        content=content
    )

    return Response({'message': '投诉已提交，管理员将尽快处理', 'complaint_id': complaint.id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaint_list_view(request):
    """获取投诉列表（管理员）"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    complaints = Complaint.objects.all().order_by('-created_at')

    # 筛选
    status_filter = request.query_params.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(complaints, request)

    result = []
    for c in result_page:
        result.append({
            'id': c.id,
            'work_order': {
                'id': c.work_order.id,
                'order_no': c.work_order.order_no
            },
            'student': {'name': c.student.name},
            'type': c.type,
            'type_display': c.get_type_display(),
            'content': c.content,
            'status': c.status,
            'status_display': c.get_status_display(),
            'created_at': c.created_at,
            'process_result': c.process_result,
            'handled_at': c.handled_at
        })

    return paginator.get_paginated_response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complaint_process_view(request, pk):
    """处理投诉"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    try:
        complaint = Complaint.objects.get(pk=pk)
    except Complaint.DoesNotExist:
        return Response({'error': '投诉不存在'}, status=status.HTTP_404_NOT_FOUND)

    result = request.data.get('result', '')
    new_status = request.data.get('status', 'resolved')

    if not result:
        return Response({'result': ['请填写处理结果']}, status=status.HTTP_400_BAD_REQUEST)

    complaint.process_result = result
    complaint.status = new_status
    complaint.handled_at = timezone.now()
    complaint.save()

    return Response({'message': '投诉已处理', 'status': new_status})
