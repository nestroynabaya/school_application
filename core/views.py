import requests
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, School, Application, Payment
from .forms import StudentRegisterForm, SchoolRegisterForm, ApplicationForm
from django.core.mail import send_mail
from django.conf import settings


# ─── Public Views ───────────────────────────────────────

def home(request):
    featured_schools = School.objects.filter(status='approved', is_featured=True)[:3]
    return render(request, 'home.html', {'featured_schools': featured_schools})


def schools(request):
    search = request.GET.get('search', '')
    region = request.GET.get('region', '')
    category = request.GET.get('category', '')

    all_schools = School.objects.filter(status='approved')

    if search:
        all_schools = all_schools.filter(name__icontains=search) | all_schools.filter(city__icontains=search)
    if region:
        all_schools = all_schools.filter(region__icontains=region)
    if category:
        all_schools = all_schools.filter(category=category)

    context = {
        'schools': all_schools,
        'category': 'All Schools',
        'category_slug': '',
        'search': search,
        'region': region,
        'selected_category': category,
    }
    return render(request, 'schools.html', context)


def schools_by_category(request, category):
    category_names = {
        'nursery': 'Nursery Schools',
        'primary': 'Primary Schools',
        'secondary': 'Secondary Schools',
        'university': 'Universities',
        'vocational': 'Vocational / Technical Schools',
    }
    search = request.GET.get('search', '')
    region = request.GET.get('region', '')

    school_list = School.objects.filter(status='approved', category=category)

    if search:
        school_list = school_list.filter(name__icontains=search) | school_list.filter(city__icontains=search)
    if region:
        school_list = school_list.filter(region__icontains=region)

    context = {
        'schools': school_list,
        'category': category_names.get(category, 'Schools'),
        'category_slug': category,
        'search': search,
        'region': region,
    }
    return render(request, 'schools.html', context)


def school_detail(request, school_id):
    school = get_object_or_404(School, id=school_id, status='approved')
    return render(request, 'apply.html', {'school': school})


# ─── Auth Views ─────────────────────────────────────────

def login_register(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'login':
            identifier = request.POST.get('email')
            password = request.POST.get('password')

            # Try email, username, then phone
            user_obj = None
            try:
                user_obj = User.objects.get(email=identifier)
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    try:
                        user_obj = User.objects.get(phone=identifier)
                    except User.DoesNotExist:
                        pass

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Incorrect password.')
            else:
                messages.error(request, 'No account found with those details.')

        elif form_type == 'register':
            form = StudentRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Please fix the errors below.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def register_school(request):
    if request.method == 'POST':
        form = SchoolRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'School registered successfully! We will review your application shortly.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'register_school.html')


# ─── Student Dashboard ───────────────────────────────────

@login_required
def dashboard(request):
    if request.user.role == 'student':
        applications = Application.objects.filter(student=request.user)
        return render(request, 'dashboards/student_dashboard.html', {'applications': applications})
    elif request.user.role == 'school':
        school = get_object_or_404(School, user=request.user)
        applications = Application.objects.filter(school=school)
        return render(request, 'dashboards/school_dashboard.html', {
            'school': school,
            'applications': applications
        })
    elif request.user.role in ['approver', 'superadmin']:
        return redirect('admin_dashboard')
    return redirect('home')


# ─── Application View ────────────────────────────────────

@login_required
def apply(request, school_id):
    school = get_object_or_404(School, id=school_id, status='approved')

    # Check if already applied
    already_applied = Application.objects.filter(
        student=request.user, school=school
    ).exists()

    if already_applied:
        messages.warning(request, 'You have already applied to this school.')
        return redirect('school_detail', school_id=school_id)

    # Check payment before allowing application
    payment_made = Payment.objects.filter(
        student=request.user, school=school, status='completed'
    ).exists()

    if request.method == 'POST' and payment_made:
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.school = school
            application.status = 'submitted'
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'apply.html', {
        'school': school,
        'form': form,
        'payment_made': payment_made,
    })


# ─── Admin Dashboard ─────────────────────────────────────

@login_required
def admin_dashboard(request):
    if request.user.role not in ['approver', 'superadmin']:
        return redirect('home')
    pending_schools = School.objects.filter(status='pending')
    all_schools = School.objects.all()
    all_applications = Application.objects.all()
    all_users = User.objects.all()
    return render(request, 'dashboards/admin_dashboard.html', {
        'pending_schools': pending_schools,
        'all_schools': all_schools,
        'all_applications': all_applications,
        'all_users': all_users,
    })


@login_required
def approve_school(request, school_id):
    if request.user.role not in ['approver', 'superadmin']:
        return redirect('home')
    school = get_object_or_404(School, id=school_id)
    school.status = 'approved'
    school.save()
    messages.success(request, f'{school.name} has been approved.')
    return redirect('admin_dashboard')


@login_required
def reject_school(request, school_id):
    if request.user.role not in ['approver', 'superadmin']:
        return redirect('home')
    school = get_object_or_404(School, id=school_id)
    school.status = 'rejected'
    school.save()
    messages.warning(request, f'{school.name} has been rejected.')
    return redirect('admin_dashboard')
    

@login_required
def update_application_status(request, application_id, status):
    if request.user.role != 'school':
        return redirect('home')
    application = get_object_or_404(Application, id=application_id, school__user=request.user)
    if status in ['accepted', 'rejected', 'under_review']:
        application.status = status
        application.save()

        # Send email notification to student
        subject = f'Application Update — {application.school.name}'
        if status == 'accepted':
            message = f'Congratulations {application.full_name}! Your application to {application.school.name} has been accepted.'
        elif status == 'rejected':
            message = f'Dear {application.full_name}, unfortunately your application to {application.school.name} was not successful.'
        else:
            message = f'Dear {application.full_name}, your application to {application.school.name} is currently under review.'

        send_mail(
            subject,
            message,
            None,
            [application.student.email],
            fail_silently=True,
        )

        messages.success(request, f'Application marked as {status} and student notified.')
    return redirect('dashboard')
    

@login_required
def initiate_payment(request, school_id):
    school = get_object_or_404(School, id=school_id, status='approved')

    # Check if already paid
    already_paid = Payment.objects.filter(
        student=request.user, school=school, status='completed'
    ).exists()

    if already_paid:
        return redirect('apply', school_id=school_id)

    tx_ref = str(uuid.uuid4())

    payload = {
        "tx_ref": tx_ref,
        "amount": str(school.application_fee),
        "currency": "UGX",
        "redirect_url": request.build_absolute_uri(f'/payment/verify/{school_id}/'),
        "customer": {
            "email": request.user.email,
            "name": request.user.get_full_name(),
            "phone_number": request.user.phone,
        },
        "customizations": {
            "title": f"Application Fee — {school.name}",
            "description": f"Pay application fee to apply to {school.name}",
        },
        "meta": {
            "tx_ref": tx_ref,
            "school_id": school_id,
            "student_id": request.user.id,
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.flutterwave.com/v3/payments",
        json=payload,
        headers=headers
    )

    data = response.json()

    if data.get('status') == 'success':
        # Save pending payment
        Payment.objects.create(
            student=request.user,
            school=school,
            amount=school.application_fee,
            transaction_id=tx_ref,
            payment_method='Flutterwave',
            status='pending'
        )
        # Redirect to Flutterwave payment page
        return redirect(data['data']['link'])
    else:
        messages.error(request, 'Payment initiation failed. Please try again.')
        return redirect('school_detail', school_id=school_id)


@login_required
def verify_payment(request, school_id):
    tx_ref = request.GET.get('tx_ref')
    status = request.GET.get('status')
    transaction_id = request.GET.get('transaction_id')

    if status == 'successful' and tx_ref:
        # Verify with Flutterwave
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        }
        response = requests.get(
            f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
            headers=headers
        )
        data = response.json()

        if data.get('status') == 'success' and data['data']['status'] == 'successful':
            # Update payment record
            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
                payment.status = 'completed'
                payment.save()
                messages.success(request, 'Payment successful! You can now fill your application.')
            except Payment.DoesNotExist:
                messages.error(request, 'Payment record not found.')
        else:
            messages.error(request, 'Payment verification failed.')
    else:
        messages.error(request, 'Payment was not completed.')

    return redirect('apply', school_id=school_id)
