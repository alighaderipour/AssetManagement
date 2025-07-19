# backend/assetmanagement/urls.py

from django.urls import path
from . import views
from .views import DepartmentListCreateView, DepartmentDetailView, CategoryListCreateView, CategoryDetailView
from rest_framework.routers import DefaultRouter
urlpatterns = [
    # Auth
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),

    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),

    # Departments
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list'),

    # Categories
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),

    # assets
    path('assets/', views.AssetListCreateView.as_view(), name='asset-list'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset-detail'),
    path('assets/<int:pk>/transfer/', views.asset_transfer_view, name='asset-transfer'),  # ✅ New route


    # Transfers
    path('transfers/', views.AssetTransferListCreateView.as_view(), name='transfer-list'),

    # Admin
    path('admin/users/', views.UserListCreateView.as_view(), name='user-list'),

    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    path('department-assets/', views.department_assets, name='department-assets'),

    path('brands/', views.brand_list, name='brand-list'),
    path('brands/<int:pk>/', views.brand_detail, name='brand-detail'),


    path('usecases/', views.usecase_list, name='usecase-list'),
    path('usecases/<int:pk>/', views.usecase_detail, name='usecase-detail'),
]
