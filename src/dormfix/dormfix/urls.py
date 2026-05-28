from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 后端 API 路由
    path('api/accounts/', include('accounts.urls')),
    path('api/repairs/', include('repairs.urls')),
    path('api/dispatch/', include('dispatch.urls')),
    path('api/maintenance/', include('maintenance.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/dashboard/', include('dashboard.urls')),

    # 前端 HTML 页面分发路由
    path('login/', TemplateView.as_view(template_name='login.html')),
    path('profile/', TemplateView.as_view(template_name='profile.html')),
    
    # 学生端页面
    path('student/orders/', TemplateView.as_view(template_name='student/dashboard.html')),
    path('student/repairs/create/', TemplateView.as_view(template_name='student/repair_request.html')),
    path('student/orders/<int:id>/', TemplateView.as_view(template_name='student/order_detail.html')),
    path('student/evaluate/<int:id>/', TemplateView.as_view(template_name='student/evaluate.html')),
    path('student/complaint/<int:id>/', TemplateView.as_view(template_name='student/complaint.html')),
    
    # 管理员端页面
    path('admin/pending-review/', TemplateView.as_view(template_name='admin/dashboard.html')),
    path('admin/pending-dispatch/', TemplateView.as_view(template_name='admin/dashboard.html')),
    path('admin/complaints/', TemplateView.as_view(template_name='admin/complaints.html')),
    path('admin/dashboard/', TemplateView.as_view(template_name='admin/statistics.html')),
    
    # 维修员端页面
    path('maintainer/tasks/', TemplateView.as_view(template_name='maintainer/dashboard.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
