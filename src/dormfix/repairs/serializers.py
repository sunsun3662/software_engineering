from rest_framework import serializers
from .models import WorkOrder, WorkOrderLog
from accounts.serializers import UserSerializer, DormRoomSerializer


class WorkOrderLogSerializer(serializers.ModelSerializer):
    operator = UserSerializer(read_only=True)

    class Meta:
        model = WorkOrderLog
        fields = ['id', 'operator', 'from_status', 'to_status', 'operation_type', 'operation_time', 'remark']


class WorkOrderListSerializer(serializers.ModelSerializer):
    """工单列表序列化器"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    room_info = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_level_display', read_only=True)

    class Meta:
        model = WorkOrder
        fields = ['id', 'order_no', 'student_name', 'room_info', 'category', 'category_display',
                  'urgency_level', 'urgency_display', 'status', 'status_display', 'submit_time', 'image']

    def get_room_info(self, obj):
        return f'{obj.room.building.building_name}-{obj.room.room_no}'


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    """工单详情序列化器"""
    student = UserSerializer(read_only=True)
    maintainer = UserSerializer(read_only=True)
    room = DormRoomSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    logs = WorkOrderLogSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = ['id', 'order_no', 'student', 'maintainer', 'room', 'category', 'category_display',
                  'description', 'image', 'urgency_level', 'urgency_display', 'status', 'status_display',
                  'submit_time', 'assign_time', 'finish_time', 'logs']


class WorkOrderCreateSerializer(serializers.ModelSerializer):
    """创建报修序列化器"""
    room_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WorkOrder
        fields = ['room_id', 'category', 'description', 'image', 'urgency_level']

    def validate_room_id(self, value):
        from accounts.models import DormRoom
        try:
            DormRoom.objects.get(id=value)
        except DormRoom.DoesNotExist:
            raise serializers.ValidationError('房间不存在')
        return value

    def create(self, validated_data):
        room_id = validated_data.pop('room_id')
        from accounts.models import DormRoom
        room = DormRoom.objects.get(id=room_id)
        order = WorkOrder.objects.create(room=room, **validated_data)

        # 记录日志
        WorkOrderLog.objects.create(
            work_order=order,
            operator=order.student,
            to_status='pending_review',
            operation_type='提交报修'
        )

        return order
