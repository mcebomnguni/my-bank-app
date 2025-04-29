from .models import BankAccount, BankCard, UserProfile
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from .forms import ServiceApplicationForm
import random
from .forms import UserProfileForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Card
from .models import BankCard
from .forms import LoanForm, InsuranceForm
from .models import Loan, Insurance
from .models import Transaction
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import BankAccount, Transaction
from django.contrib.auth.decorators import login_required
from .forms import PinVerificationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import BankAccount, BankCard
from .forms import PinVerificationForm


@login_required
def transfer_funds(request):
    if request.method == 'POST':
        recipient_account_number = request.POST.get('recipient_account')
        recipient_bank = request.POST.get('recipient_bank', '')
        amount = float(request.POST.get('amount'))

        # Get the sender's account
        try:
            sender_account = BankAccount.objects.get(user=request.user)
        except BankAccount.DoesNotExist:
            messages.error(request, "Your account does not exist.")
            return redirect('dashboard')

        # Check if the sender has enough balance
        if sender_account.balance < amount:
            messages.error(request, "Insufficient funds.")
            return redirect('dashboard')

        # Try to find the recipient account (internal transfer)
        try:
            recipient_account = BankAccount.objects.get(account_number=recipient_account_number)
            is_internal = True
        except BankAccount.DoesNotExist:
            recipient_account = None
            is_internal = False  

        # Deduct the amount from the sender's account
        sender_account.balance -= amount
        sender_account.save()

        # Handle the recipient account:
        if is_internal:
            recipient_account.balance += amount
            recipient_account.save()
            transaction_status = 'Completed'  
        else:
            transaction_status = 'Pending' 

        # Save the transaction record
        Transaction.objects.create(
            user=request.user,
            from_account=sender_account,
            to_account_number=recipient_account_number,
            to_bank=recipient_bank,
            amount=amount,
            transaction_type='transfer',
            status=transaction_status
        )

        # Success message
        if is_internal:
            messages.success(request, f"${amount:.2f} sent to account {recipient_account_number}.")
        else:
            messages.success(request, f"${amount:.2f} sent to account {recipient_account_number} at {recipient_bank}. Transaction is pending.")

        return redirect('dashboard')

    return render(request, 'banking_app/transfer_funds.html')


def reserve_funds(request):
    if request.method == 'POST':
        amount = request.POST['amount']

        # Reserve funds logic goes here
        transaction = Transaction(user=request.user, transaction_type='reserve', amount=amount)
        transaction.save()

        return redirect('reserve_success')
    return render(request, 'banking_app/reserve_funds.html')


@login_required
def bank_cards(request):
    cards = BankCard.objects.filter(user=request.user)
    return render(request, 'banking_app/bank_cards.html', {'cards': cards})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create BankAccount for new user
            BankAccount.objects.create(
                user=user,
                account_number=generate_account_number(),
                balance=00.00 
            )
            login(request, user)
            return redirect('complete_profile')
    else:
        form = SignUpForm()
    return render(request, 'banking_app/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'banking_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    try:
        # Get the user's bank account
        account = BankAccount.objects.get(user=request.user)
        
        # Get the cards associated with the user's account
        cards = BankCard.objects.filter(account=account)

        # If no cards are available, display an appropriate message
        if not cards.exists():
            return render(request, 'banking_app/dashboard.html', {
                'account': account,
                'error': 'No cards available yet.',
            })

    except BankAccount.DoesNotExist:
        # If the bank account does not exist for the user, show an error message
        return render(request, 'banking_app/dashboard.html', {
            'error': 'No bank account found for your account.',
        })

    # Render the dashboard with account and card information
    return render(request, 'banking_app/dashboard.html', {
        'account': account,
        'cards': cards,
    })

    
@login_required
def reveal_card(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    return render(request, 'banking_app/reveal_card.html', {'card': card})


@login_required
def services(request):
    loan_form = LoanForm()
    insurance_form = InsuranceForm()
    return render(request, 'banking_app/services.html', {
        'loan_form': loan_form,
        'insurance_form': insurance_form
    })


@login_required
def support(request):
    return render(request, 'banking_app/support.html')


def generate_account_number():
    return str(random.randint(100000000000, 199999999999))


def generate_card_number():
    return str(random.randint(4000000000000000, 4999999999999999)) 


def generate_cvv():
    return str(random.randint(100, 999))


@login_required
def complete_profile(request):
    user = request.user

    if hasattr(user, 'userprofile'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()

            # Create bank account if not exists
            account, created = BankAccount.objects.get_or_create(
                user=user,
                defaults={'account_number': generate_account_number(), 'balance': 0.00}
            )

            # Only create card if one doesn't already exist
            if not BankCard.objects.filter(account=account).exists():
                BankCard.objects.create(
                    user=user,
                    account=account,
                    card_type='Visa',
                    card_number=generate_card_number(),
                    cvv=generate_cvv(),
                    expiry_date='12/30',
                    pin=form.cleaned_data['pin']
                )

                # Send email
                send_mail(
                    subject="🎉 Welcome to Capstone Bank!",
                    message=f"Hello {profile.full_name}, your account number is {account.account_number}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )

            return redirect('dashboard')
    else:
        form = UserProfileForm()

    return render(request, 'banking_app/complete_profile.html', {'form': form})


def apply_for_loan(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user  
            loan.save()
            return redirect('loan_success')  
    else:
        form = LoanForm()
    
    return render(request, 'banking_app/apply_for_loan.html', {'form': form})


def apply_for_insurance(request):
    if request.method == 'POST':
        form = InsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save(commit=False)
            insurance.user = request.user
            insurance.save()
            return redirect('insurance_success')
    else:
        form = InsuranceForm()

    return render(request, 'bankking_app/apply_for_insurance.html', {'form': form})


def view_card_details(request):
    if request.method == 'POST':
        entered_pin = request.POST['pin']
        user_pin = request.user.profile.pin  

        if entered_pin == user_pin:
            card_details = get_card_details(request.user)  
            return render(request, 'card_details.html', {'card_details': card_details})
        else:
            error = "Incorrect PIN. Please try again."
            return render(request, 'card_details.html', {'error': error})
    
    return render(request, 'banking_app/card_details.html')


def loan_success(request):
    # Add any logic for loan success here if needed
    return render(request, 'banking_app/loan_success.html')


def insurance_success(request):
    return render(request, 'banking_app/insurance_success.html')


@login_required
def reveal_card(request, card_id):
    # Fetch the card based on the card_id and the user
    card = get_object_or_404(Card, id=card_id, user=request.user)

    # Handle the PIN verification process
    if request.method == 'POST':
        form = PinVerificationForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data['pin']
            user_pin = request.user.profile.pin  

            if entered_pin == user_pin:
                # Correct PIN, show card back details
                return render(request, 'banking_app/reveal_card.html', {
                    'card': card,  
                    'pin_verified': True
                })
            else:
                # Incorrect PIN, show error message
                messages.error(request, "Incorrect PIN. Please try again.")
                form = PinVerificationForm()  
        else:
            form = PinVerificationForm()
    else:
        form = PinVerificationForm()

    return render(request, 'banking_app/reveal_card.html', {'form': form, 'card': card})


def verify_pin(request):
    # Get the number of attempts from the session
    attempts = request.session.get('pin_attempts', 0)

    if request.method == 'POST':
        form = PinVerificationForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']  
            user_profile = request.user.userprofile  

            # Check if the PIN is correct (Verify against the BankCard's PIN)
            try:
                # Retrieve the user's bank account
                account = BankAccount.objects.get(user=request.user)

                # Retrieve the associated BankCard (assuming one card per account, modify if needed)
                card = BankCard.objects.get(account=account)

                if card.pin == pin:  
                    # If PIN is correct, reset the attempts counter in the session
                    request.session['pin_attempts'] = 0

                    # If PIN is correct, fetch cards related to the account
                    cards = BankCard.objects.filter(account=account)

                    return render(request, 'banking_app/dashboard.html', {
                        'account': account,
                        'cards': cards,
                        'show_back': True,  
                        'now': timezone.now(),
                    })
                else:
                    # Increment the failed attempts count
                    attempts += 1
                    request.session['pin_attempts'] = attempts

                    # Show error and remaining attempts
                    if attempts >= 3:
                        messages.error(request, "You have exceeded the maximum number of attempts. Please try again later.")
                    else:
                        messages.error(request, f"Incorrect PIN. You have {3 - attempts} attempt(s) remaining.")

            except BankAccount.DoesNotExist:
                messages.error(request, 'No bank account found.')
            except BankCard.DoesNotExist:
                messages.error(request, 'No card associated with this account.')

        else:
            messages.error(request, 'Please enter a valid PIN.')

    else:
        form = PinVerificationForm()

    # If there are attempts remaining, show the form, else lock the user out
    if attempts >= 3:
        return render(request, 'banking_app/dashboard.html', {
            'error': 'You have exceeded the maximum number of PIN attempts.',
            'form': form
        })
    
    return render(request, 'banking_app/dashboard.html', {'form': form})
