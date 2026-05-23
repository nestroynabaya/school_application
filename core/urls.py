from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('schools/', views.schools, name='schools'),
    path('apply/<int:school_id>/', views.apply, name='apply'),
    path('login/', views.login_register, name='login'),
    path('register-school/', views.register_school, name='register_school'),
]
