from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('buildings/', views.building_list_view, name='building-list'),
    path('rooms/', views.room_list_view, name='room-list'),
    path('users/', views.user_list_create_view, name='user-list-create'),
    path('users/<int:pk>/', views.user_detail_view, name='user-detail'),
]
