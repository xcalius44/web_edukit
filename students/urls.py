from django.urls import path
from . import views

urlpatterns = [
    # Registration
    path('register/student/', views.StudentRegistrationView.as_view(), name='student_registration'),
    path('register/teacher/', views.TeacherRegistrationView.as_view(), name='teacher_registration'),

    # Enrollment
    path('enroll-course/', views.StudentEnrollCourseView.as_view(), name='student_enroll_course'),

    # Student course views
    path('courses/', views.StudentCourseListView.as_view(), name='student_course_list'),
    path('course/<pk>/', views.StudentCourseDetailView.as_view(), name='student_course_detail'),
    path('course/<pk>/<module_id>/', views.StudentCourseDetailView.as_view(), name='student_course_detail_module'),

    # Teacher profile view
    path('teacher/<int:pk>/', views.TeacherProfileView.as_view(), name='teacher_profile'),
    path('teacher/<int:pk>/edit/', views.TeacherProfileEditView.as_view(), name='teacher_profile_edit'),
]
