from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list, name='list'),
    path('create/', views.review_create, name='create'),
    path('success/', views.review_success, name='success'),
]