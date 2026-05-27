from django.urls import path
from . import views

urlpatterns = [
    path('statistics/', views.statistics_view, name='statistics'),
    path('export/', views.export_view, name='export'),
]
