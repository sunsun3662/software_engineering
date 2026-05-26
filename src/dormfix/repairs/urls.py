from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list_create_view, name='order-list-create'),
    path('<int:pk>/', views.order_detail_view, name='order-detail'),
    path('<int:pk>/cancel/', views.order_cancel_view, name='order-cancel'),
]
