from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ServiceApplication
from .models import UserProfile
from django import forms
from .models import Loan, Insurance


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ServiceApplicationForm(forms.ModelForm):
    class Meta:
        model = ServiceApplication
        fields = ['service_type', 'full_name', 'email', 'income']


class UserProfileForm(forms.ModelForm):
    pin = forms.CharField(max_length=4, widget=forms.PasswordInput(), label="Choose a 4-digit PIN")
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    citizenship = forms.CharField(max_length=50, required=True)
    identity_number = forms.CharField(max_length=30, required=True)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'date_of_birth', 'citizenship', 'identity_number', 'pin']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'term_years']


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['insurance_type', 'coverage_amount', 'duration_years']


class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'date_of_birth', 'citizenship', 'identity_number', 'phone_number', 'pin']


class PinVerificationForm(forms.Form):
    pin = forms.CharField(max_length=4, widget=forms.PasswordInput(), label="Enter your 4-digit PIN")
