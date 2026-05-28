from django.urls import path
from . import views
from .views import CourseStudioView

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('mine/', views.ManageCourseListView.as_view(), name='manage_course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    # Content management
    path('module/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(), name='module_content_create'),
    path('module/<int:module_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(), name='module_content_update'),
    path('content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='module_content_delete'),
    path('module/<int:module_id>/', views.ModuleContentListView.as_view(), name='module_content_list'),
    path('module/order/', views.ModuleOrderView.as_view(), name='module_order'),
    path('content/order/', views.ContentOrderView.as_view(), name='content_order'),

    # Course list + detail
    path('subject/<slug:subject>/', views.CourseListView.as_view(), name='course_list_subject'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),

    # Publishing
    path('course/<int:pk>/publish/', views.PublishCourseView.as_view(), name='course_publish'),
    path('course/<int:pk>/unpublish/', views.UnpublishCourseView.as_view(), name='course_unpublish'),

    # ⭐ FINAL STUDIO URLS (ONLY THESE!)
    path('studio/<int:course_id>/', CourseStudioView.as_view(), name='course_studio'),
    path('studio/<int:course_id>/<int:lesson_id>/', CourseStudioView.as_view(), name='course_studio_lesson'),
]
