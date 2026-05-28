from rest_framework import serializers
from .models import User, DormBuilding, DormRoom


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'account', 'name', 'student_or_staff_no', 'phone', 'role', 'role_display', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=128)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'account', 'name', 'password', 'role', 'role_display', 'student_or_staff_no', 'phone', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_account(self, value):
        if User.objects.filter(account=value).exists():
            raise serializers.ValidationError('该账号已存在')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['username'] = validated_data['account']
        user = User.objects.create_user(password=password, **validated_data)
        return user


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
