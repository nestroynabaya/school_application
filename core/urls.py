from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('schools/', views.schools, name='schools'),
    path('apply/<int:school_id>/', views.apply, name='apply'),
]
