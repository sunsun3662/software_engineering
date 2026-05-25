from rest_framework import serializers
from .models import User, DormBuilding, DormRoom


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'account', 'name', 'student_or_staff_no', 'phone', 'role', 'role_display', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128)


class DormBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DormBuilding
        fields = ['id', 'building_code', 'building_name', 'gender_limit']


class DormRoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.building_name', read_only=True)

    class Meta:
        model = DormRoom
        fields = ['id', 'building', 'building_name', 'room_no', 'floor_no']
