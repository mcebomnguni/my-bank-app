from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ServiceApplication
from .models import UserProfile
from django import forms
from .models import Loan, Insurance


class SignUpForm(UserCreationForm):
    """
    A form for registering new users.

    Extends Django's built-in UserCreationForm to include an email field. Creates a new user
    with a username, email, and password.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ServiceApplicationForm(forms.ModelForm):
    """
    A form to apply for a general banking service (e.g., loans, insurance).

    Captures user information such as full name, email, income, and selected service type.
    """
    class Meta:
        model = ServiceApplication
        fields = ['service_type', 'full_name', 'email', 'income']


class UserProfileForm(forms.ModelForm):
    """
    A form to complete the user's profile with personal and identification details.

    Includes fields for full name, phone number, date of birth, citizenship, ID number,
    and a 4-digit secure PIN for account access and transactions.
    """
    pin = forms.CharField(max_length=4, widget=forms.PasswordInput(), label="Choose a 4-digit PIN")
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    citizenship = forms.CharField(max_length=50, required=True)
    identity_number = forms.CharField(max_length=30, required=True)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'date_of_birth', 'citizenship', 'identity_number', 'pin']


class SignUpForm(UserCreationForm):
    """
    A form for users to apply for a loan.

    Collects loan type, requested loan amount, and loan term (in years).
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoanForm(forms.ModelForm):
    """
    A form for users to apply for a loan.

    Collects loan type, requested loan amount, and loan term (in years).
    """
    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'term_years']


class InsuranceForm(forms.ModelForm):
     """
    A form for users to apply for insurance.

    Captures the insurance type, coverage amount, and duration (in years).
    """
    class Meta:
        model = Insurance
        fields = ['insurance_type', 'coverage_amount', 'duration_years']


class CompleteProfileForm(forms.ModelForm):
    """
    A form used to complete the user profile after registration.

    Collects identity verification and contact details including full name, date of birth,
    citizenship, identity number, phone number, and PIN.
    """
    class Meta:
        model = UserProfile
        fields = ['full_name', 'date_of_birth', 'citizenship', 'identity_number', 'phone_number', 'pin']


class PinVerificationForm(forms.Form):
    """
    A form for verifying the user's 4-digit PIN.

    Used to confirm user identity before displaying or allowing sensitive operations,
    such as revealing card details.
    """
    pin = forms.CharField(max_length=4, widget=forms.PasswordInput(), label="Enter your 4-digit PIN")
