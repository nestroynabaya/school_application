from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('school', 'School'),
        ('approver', 'Approver Admin'),
        ('superadmin', 'Super Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# School model
class School(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    CATEGORY_CHOICES = [
        ('nursery', 'Nursery'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('university', 'University'),
        ('vocational', 'Vocational / Technical'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    registration_number = models.CharField(max_length=100, unique=True)
    year_established = models.IntegerField()
    description = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    reg_certificate = models.FileField(upload_to='school_docs/')
    other_doc = models.FileField(upload_to='school_docs/', blank=True, null=True)
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Payment model
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_method = models.CharField(max_length=50)  # e.g. Mobile Money, Card
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.school.name} - {self.status}"


# Application model
class Application(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='applications')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='application')
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    programme = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=255)
    guardian_phone = models.CharField(max_length=20)
    previous_school = models.CharField(max_length=255, blank=True)
    results_certificate = models.FileField(upload_to='application_docs/')
    birth_certificate = models.FileField(upload_to='application_docs/')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} → {self.school.name} ({self.status})"
