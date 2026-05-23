from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def schools(request):
    return render(request, 'schools.html')

def apply(request, school_id):
    return render(request, 'apply.html')

def login_register(request):
    return render(request, 'login.html')

def register_school(request):
    return render(request, 'register_school.html')
