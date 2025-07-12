# backend/propertycontrol/views.py

from rest_framework.exceptions import ValidationError
from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser

from .models import User, Department, Category, Asset, AssetTransfer, Brand
from .serializers import (
    UserSerializer, LoginSerializer, DepartmentSerializer,
    CategorySerializer, AssetSerializer, AssetTransferSerializer,
    AssetTransferCreateSerializer, BrandSerializer
)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'


# --------------------
# Authentication Views
# --------------------

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful"})
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    return Response(UserSerializer(request.user).data)


# --------------------
# Departments
# --------------------

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


# --------------------
# Categories
# --------------------

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


# --------------------
# Assets
# --------------------

class AssetListCreateView(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            print("🔴 Asset validation error:", e.detail)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        queryset = Asset.objects.all()
        search = self.request.query_params.get('search', None)
        department = self.request.query_params.get('department', None)
        category = self.request.query_params.get('category', None)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )

        if department:
            queryset = queryset.filter(current_department__id=department)

        if category:
            queryset = queryset.filter(category__id=category)

        return queryset


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]


# ✅ Asset Transfer via PUT /assets/<pk>/transfer/
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def asset_transfer_view(request, pk):
    # Support for multipart/form-data
    if request.content_type.startswith('multipart/'):
        # DRF does NOT automatically attach .FILES for function-based views, but running _load_post_and_files helps.
        request._load_post_and_files()

    try:
        asset = Asset.objects.get(pk=pk)
    except Asset.DoesNotExist:
        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)

    new_department_id = request.data.get("department")
    if not new_department_id:
        return Response({"error": "Department ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_department = Department.objects.get(pk=new_department_id)
    except Department.DoesNotExist:
        return Response({"error": "Target department does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # New: Get price/image from request
    price = request.data.get("price")  # may be string, cast/validate as needed
    image = request.FILES.get("image")  # file object or None

    # New: Get notes too (optional)
    notes = request.data.get("notes", "")

    AssetTransfer.objects.create(
        asset=asset,
        from_department=asset.current_department,
        to_department=new_department,
        transferred_by=request.user,
        price=price if price is not None and price != "" else None,
        image=image if image is not None else None,
        notes=notes,
    )

    asset.current_department = new_department
    asset.save()

    return Response(AssetSerializer(asset).data, status=status.HTTP_200_OK)


# --------------------
# Transfers
# --------------------

class AssetTransferListCreateView(generics.ListCreateAPIView):
    queryset = AssetTransfer.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssetTransferCreateSerializer
        return AssetTransferSerializer

    def get_queryset(self):
        queryset =AssetTransfer.objects.all()
        asset_id = self.request.query_params.get('asset', None)

        if asset_id:
            queryset = queryset.filter(asset__id=asset_id)

        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_transfers(request):
    limit = request.query_params.get('limit', 5)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 5

    transfers = AssetTransfer.objects.order_by('-transfer_date')[:limit]
    serializer = AssetTransferSerializer(transfers, many=True)
    return Response(serializer.data)


# --------------------
# Dashboard
# --------------------

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    stats = {
        'total_assets': Asset.objects.count(),
        'active_assets': Asset.objects.filter(status='active').count(),
        'total_departments': Department.objects.count(),
        'total_categories': Category.objects.count(),
        'recent_transfers': AssetTransferSerializer(
            AssetTransfer.objects.order_by('-transfer_date')[:5],
            many=True
        ).data,
        'assets_by_department': {}
    }

    for dept in Department.objects.all():
        stats['assets_by_department'][dept.name] = Asset.objects.filter(
            current_department=dept
        ).count()

    return Response(stats)


# --------------------
# Admin - Users
# --------------------

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated()]


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_assets(request):
    search = request.query_params.get('search', '')
    from .models import Department, Asset

    departments = Department.objects.all()
    if search:
        departments = departments.filter(name__icontains=search)

    result = []
    for dept in departments:
        assets = Asset.objects.filter(current_department=dept)
        asset_data = [
            {
                "asset_id": a.id,
                "name": a.name,
                "code": a.asset_code,
                "current_value": a.current_value,
            }
            for a in assets
        ]
        if asset_data:
            result.append({
                "department_id": dept.id,
                "department_name": dept.name,
                "assets": asset_data
            })
    return Response(result)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def brand_list(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def brand_detail(request, pk):
    try:
        brand = Brand.objects.get(pk=pk)
    except Brand.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BrandSerializer(brand)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = BrandSerializer(brand, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        brand.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)