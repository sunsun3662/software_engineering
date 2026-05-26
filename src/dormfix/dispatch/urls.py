from django.urls import path
from . import views

urlpatterns = [
    path('pending-review/', views.pending_review_list_view, name='pending-review-list'),
    path('<int:pk>/approve/', views.approve_view, name='order-approve'),
    path('<int:pk>/reject/', views.reject_view, name='order-reject'),
    path('pending-dispatch/', views.pending_dispatch_list_view, name='pending-dispatch-list'),
    path('maintainers/', views.maintainer_list_view, name='maintainer-list'),
    path('<int:pk>/assign/', views.assign_view, name='order-assign'),
]
