from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('schools/', views.schools, name='schools'),
    path('schools/category/<str:category>/', views.schools_by_category, name='schools_by_category'),
    path('schools/<int:school_id>/', views.school_detail, name='school_detail'),
    path('apply/<int:school_id>/', views.apply, name='apply'),
    path('login/', views.login_register, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register-school/', views.register_school, name='register_school'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/approve/<int:school_id>/', views.approve_school, name='approve_school'),
    path('admin-dashboard/reject/<int:school_id>/', views.reject_school, name='reject_school'),
    path('application/<int:application_id>/status/<str:status>/', views.update_application_status, name='update_application_status'),
    path('payment/initiate/<int:school_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/<int:school_id>/', views.verify_payment, name='verify_payment'),
]
