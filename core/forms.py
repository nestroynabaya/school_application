from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, School, Application, Payment

class StudentRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'student'
        if commit:
            user.save()
        return user


class SchoolRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = School
        fields = [
            'name', 'category', 'registration_number', 'year_established',
            'description', 'city', 'region', 'address', 'phone',
            'application_fee', 'logo', 'reg_certificate', 'other_doc'
        ]

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # Create the user account first
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password1'],
            role='school'
        )
        school = super().save(commit=False)
        school.user = user
        school.email = self.cleaned_data['email']
        if commit:
            school.save()
        return school


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'full_name', 'date_of_birth', 'gender', 'programme',
            'guardian_name', 'guardian_phone', 'previous_school',
            'results_certificate', 'birth_certificate', 'notes'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
