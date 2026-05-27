from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.task_list_view, name='task-list'),
    path('<int:pk>/accept/', views.accept_task_view, name='task-accept'),
    path('<int:pk>/complete/', views.complete_task_view, name='task-complete'),
    path('<int:pk>/confirm/', views.confirm_task_view, name='task-confirm'),
]
