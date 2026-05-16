from django.shortcuts import render

# Create your views here.
# Homepage
def home(request):
    return render(request, 'home.html')

# Schools listing page
def schools(request):
    return render(request, 'schools.html')

# Application form page
def apply(request, school_id):
    return render(request, 'apply.html')
