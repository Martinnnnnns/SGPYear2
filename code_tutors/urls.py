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
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_student_list/', views.admin_student_list, name='admin_student_list'),
    path('admin_tutor_list/', views.admin_tutor_list, name='admin_tutor_list'),
    path('admin_bookings_list/', views.admin_bookings_list, name='admin_bookings_list'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('request_lesson/', views.request_lesson, name='request_lesson'),  
    path('student_profile/', views.student_profile, name='student_profile'),  
    path('student_support/', views.student_support, name='student_support'),  
    path('download_invoice/<int:invoice_id>/', views.download_invoice, name='download_invoice'),
    path('tutor_page/', views.tutor_page, name='tutor_page'),
    path('tutor_page/schedule_sessions', views.schedule_sessions, name='schedule_sessions'),
    path('tutor_page/reports', views.reports, name='reports'),
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)