from django.db.models import Sum
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Department, Category, Asset, AssetTransfer, Brand
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name',
            'last_name', 'role', 'department', 'phone'
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


    def validate(self, data):
        user = authenticate(
            username=data.get('username'),
            password=data.get('password')
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        data['user'] = user
        return data


class DepartmentSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(
        source='manager.get_full_name', read_only=True
    )

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'manager','type',
            'manager_name', 'description', 'created_at'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'description']


class AssetSerializer(serializers.ModelSerializer):
    total_transfer_cost = serializers.SerializerMethodField()
    current_value = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    department_name = serializers.CharField(
        source='department.name', read_only=True
    )
    current_department_name = serializers.CharField(
        source='current_department.name', read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True
    )
    current_department_type = serializers.CharField(
        source='current_department.type', read_only=True
    )

    class Meta:
        model = Asset
        fields = [
            'id', 'code', 'name', 'description',
            'category', 'department', 'current_department',
            'status', 'purchase_date', 'purchase_price',
            'current_value', 'serial_number','asset_code', 'brand', 'model',
            'image', 'category_name', 'department_name',
            'current_department_name', 'created_by',
            'created_by_name', 'created_at', 'updated_at',
            'total_transfer_cost', 'current_department_type',

        ]
        read_only_fields = ['code', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        # auto-set the creator
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def get_total_transfer_cost(self, obj):
        transfers = obj.assettransfer_set.aggregate(total=Sum('price'))
        return transfers['total'] or 0


class AssetTransferSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(
        source='asset.name', read_only=True
    )
    asset_code = serializers.CharField(
        source='asset.asset_code', read_only=True
    )
    from_department_name = serializers.CharField(
        source='from_department.name', read_only=True
    )
    to_department_name = serializers.CharField(
        source='to_department.name', read_only=True
    )
    transferred_by_name = serializers.CharField(
        source='transferred_by.get_full_name', read_only=True
    )

    class Meta:
        model = AssetTransfer
        fields = [
            'id',
            'asset',
            'asset_name',
            'asset_code',
            'from_department',
            'from_department_name',
            'to_department',
            'to_department_name',
            'transfer_date',
            'notes',
            'transferred_by',
            'transferred_by_name',
            'price',
            'image'
        ]

class AssetTransferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTransfer
        fields = ['asset', 'to_department', 'notes', 'price', 'image']

    def create(self, validated_data):
        asse = validated_data['asset']
        validated_data['from_department'] = asse.current_department
        validated_data['transferred_by'] = self.context['request'].user
        transfer = super().create(validated_data)
        # update the asset's department
        asse.current_department = validated_data['to_department']
        asse.save()
        return transfer

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['code']
