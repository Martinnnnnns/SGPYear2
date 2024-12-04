"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from tutorials import views




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.LogoutView.as_view(), name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path("access_denied", views.AccessDeniedView.as_view(), name="access_denied"),
    path('admin_student_list/', views.AdminStudentListView.as_view(), name='admin_student_list'),
    path('admin_tutor_list/', views.AdminTutorListView.as_view(), name='admin_tutor_list'),
    path('admin_bookings_list/', views.AdminBookingsListView.as_view(), name='admin_bookings_list'),
    path("admin-review/", views.AdminReviewRequestsView.as_view(), name="admin_review_requests"),
    path('request_change_bookings/<int:lesson_id>/', views.RequestChangeBookingsView.as_view(), name='request_change_bookings'),
    path('request_cancel_bookings/<int:lesson_id>/', views.RequestCancelBookingsView.as_view(), name='request_cancel_bookings'),
    path('request_lesson/', views.MakeLessonRequestView.as_view(), name='request_lesson'), 
    path('request_made/', views.LessonMadeView.as_view(), name='request_made'),  
    path('student_profile/', views.StudentProfileView.as_view(), name='student_profile'),  
    path('student_support/', views.StudentSupportView.as_view(), name='student_support'),  
    path('download_invoice/<int:invoice_id>/', views.download_invoice, name='download_invoice'),
    path('lesson/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('schedule_sessions/', views.schedule_sessions, name='schedule_sessions'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('trigger_matching/', views.TriggerMatchingView.as_view(), name='trigger_matching'),
    path('tutor_page/delete_availability/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('tutor_student_list/students/' , views.StudentListView.as_view(), name = 'student_list'),
    path('confirm_delete/<int:slot_id>/', views.confirm_delete_availability, name='confirm_delete_availability'),
    path('confirm_delete_all/', views.confirm_delete_all_availabilities, name='confirm_delete_all_availabilities'),
    path('tutor_page/delete_availability/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('tutor/lessons/', views.TutorLessonsView.as_view(), name='tutor_lessons'),

    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)