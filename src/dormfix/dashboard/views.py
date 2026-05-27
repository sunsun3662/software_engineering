from datetime import timedelta
from django.db.models import Count, Avg
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from repairs.models import WorkOrder
from feedback.models import Evaluation


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_view(request):
    """获取统计数据 (UC012)"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    # 筛选条件
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    building_id = request.query_params.get('building')
    category = request.query_params.get('category')

    orders = WorkOrder.objects.all()
    if start_date:
        orders = orders.filter(submit_time__date__gte=start_date)
    if end_date:
        orders = orders.filter(submit_time__date__lte=end_date)
    if building_id:
        orders = orders.filter(room__building_id=building_id)
    if category:
        orders = orders.filter(category=category)

    # 汇总数据
    total_orders = orders.count()
    completed_orders = orders.filter(status__in=['completed', 'evaluated']).count()
    completion_rate = round(completed_orders / total_orders * 100, 1) if total_orders > 0 else 0

    # 平均响应时长（小时）- 用Python计算
    assigned_orders = orders.filter(assign_time__isnull=False, submit_time__isnull=False)
    avg_response_hours = 0
    if assigned_orders.exists():
        total_hours = 0
        count = 0
        for o in assigned_orders[:100]:  # 限制计算量
            diff = (o.assign_time - o.submit_time).total_seconds() / 3600
            total_hours += diff
            count += 1
        avg_response_hours = round(total_hours / count, 1) if count > 0 else 0

    # 平均完成时长（小时）
    finished_orders = orders.filter(finish_time__isnull=False, submit_time__isnull=False)
    avg_completion_hours = 0
    if finished_orders.exists():
        total_hours = 0
        count = 0
        for o in finished_orders[:100]:
            diff = (o.finish_time - o.submit_time).total_seconds() / 3600
            total_hours += diff
            count += 1
        avg_completion_hours = round(total_hours / count, 1) if count > 0 else 0

    urgent_orders = orders.filter(urgency_level='urgent').count()

    # 类别分布
    category_dist = list(orders.values('category').annotate(count=Count('id')).order_by('-count'))

    # 状态分布
    status_dist = list(orders.values('status').annotate(count=Count('id')).order_by('-count'))

    # 每日趋势（最近7天）
    today = timezone.now().date()
    daily_trend = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = orders.filter(submit_time__date=date).count()
        daily_trend.append({'date': str(date), 'count': count})

    # 维修人员绩效
    from accounts.models import User
    maintainers = User.objects.filter(role='maintainer')
    maintainer_perf = []
    for m in maintainers:
        m_orders = orders.filter(maintainer=m, status__in=['completed', 'evaluated'])
        completed_count = m_orders.count()
        avg_hours = 0
        avg_score = 0
        if completed_count > 0:
            # 计算平均时长
            total_hours = 0
            for o in m_orders[:50]:
                if o.finish_time and o.submit_time:
                    total_hours += (o.finish_time - o.submit_time).total_seconds() / 3600
            avg_hours = round(total_hours / completed_count, 1) if completed_count > 0 else 0

            # 计算平均评分
            evaluations = Evaluation.objects.filter(work_order__maintainer=m)
            if evaluations.exists():
                avg_score = round(evaluations.aggregate(avg=Avg('speed_score'))['avg'] or 0, 1)

        maintainer_perf.append({
            'maintainer': m.name,
            'completed_count': completed_count,
            'avg_hours': avg_hours,
            'avg_score': avg_score
        })

    # 满意度分布
    satisfaction_dist = list(
        Evaluation.objects.filter(work_order__in=orders)
        .values('speed_score')
        .annotate(count=Count('id'))
        .order_by('speed_score')
    )
    satisfaction_dist = [{'score': item['speed_score'], 'count': item['count']} for item in satisfaction_dist]

    return Response({
        'summary': {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'completion_rate': completion_rate,
            'avg_response_hours': avg_response_hours,
            'avg_completion_hours': avg_completion_hours,
            'urgent_orders': urgent_orders
        },
        'category_distribution': category_dist,
        'status_distribution': status_dist,
        'daily_trend': daily_trend,
        'maintainer_performance': maintainer_perf,
        'satisfaction_distribution': satisfaction_dist
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_view(request):
    """导出Excel报表"""
    if not request.user.is_admin:
        return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '工单统计'

    # 表头
    headers = ['工单编号', '报修人', '宿舍', '类别', '状态', '提交时间', '完成时间']
    ws.append(headers)

    # 数据
    orders = WorkOrder.objects.all().order_by('-submit_time')
    for order in orders[:100]:
        ws.append([
            order.order_no,
            order.student.name,
            f'{order.room.building.building_name}-{order.room.room_no}',
            order.get_category_display(),
            order.get_status_display(),
            str(order.submit_time),
            str(order.finish_time) if order.finish_time else ''
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    wb.save(response)
    return response
