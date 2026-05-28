from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('products/', views.product_list, name='products'),
    path('products/add/', views.product_create, name='product_create'),
    path('orders/', views.order_list, name='orders'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/<str:status>/', views.order_update_status, name='order_update_status'),
    path('orders/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('customer/<int:user_id>/history/', views.customer_history, name='customer_history'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('users/', views.user_list, name='user_list'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('settings/', views.user_settings, name='user_settings'),
]
