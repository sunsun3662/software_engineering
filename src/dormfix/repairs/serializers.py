from rest_framework import serializers
from .models import WorkOrder, WorkOrderLog, WorkOrderImage


class WorkOrderLogSerializer(serializers.ModelSerializer):
    """工单日志序列化器"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)

    class Meta:
        model = WorkOrderLog
        fields = ['operation_type', 'operator_name', 'operation_time', 'remark']


class WorkOrderListSerializer(serializers.ModelSerializer):
    """工单列表序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    urgency_level_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = ['id', 'order_no', 'category', 'category_display', 'description',
                  'urgency_level', 'urgency_level_display', 'status', 'status_display',
                  'submit_time', 'student', 'room']

    def get_student(self, obj):
        return {'name': obj.student.name, 'phone': obj.student.phone}

    def get_room(self, obj):
        return {
            'building_name': obj.room.building.building_name,
            'room_no': obj.room.room_no
        }


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    """工单详情序列化器"""
    student = serializers.SerializerMethodField()
    maintainer = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    urgency_level_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    image_urls = serializers.SerializerMethodField()
    logs = WorkOrderLogSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = ['id', 'order_no', 'student', 'maintainer', 'room', 'category', 'category_display',
                  'description', 'image_urls', 'urgency_level', 'urgency_level_display',
                  'status', 'status_display', 'submit_time', 'assign_time', 'finish_time', 'logs']

    def get_student(self, obj):
        return {'name': obj.student.name, 'phone': obj.student.phone}

    def get_maintainer(self, obj):
        if obj.maintainer:
            return {'name': obj.maintainer.name, 'phone': obj.maintainer.phone}
        return None

    def get_room(self, obj):
        return {'building_name': obj.room.building.building_name, 'room_no': obj.room.room_no}

    def get_image_urls(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()] if request else [img.image.url for img in obj.images.all()]
