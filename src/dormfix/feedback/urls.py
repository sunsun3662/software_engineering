from django.urls import path
from . import views

urlpatterns = [
    path('evaluate/<int:work_order_id>/', views.evaluate_view, name='evaluate'),
    path('complaint/<int:work_order_id>/', views.complaint_create_view, name='complaint-create'),
    path('complaints/', views.complaint_list_view, name='complaint-list'),
    path('complaints/<int:pk>/process/', views.complaint_process_view, name='complaint-process'),
]
