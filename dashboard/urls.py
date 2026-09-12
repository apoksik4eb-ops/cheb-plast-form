from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHome.as_view(), name='home'),
    path('orders/', views.OrderList.as_view(), name='orders'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order_detail'),
    path('orders/<int:pk>/cancel/', views.order_cancel, name='order_cancel'),
    path('orders/<int:pk>/repeat/', views.order_repeat, name='order_repeat'),
]