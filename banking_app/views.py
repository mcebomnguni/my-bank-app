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
    """
    Handle transferring funds between bank accounts.

    Allows the logged-in user to transfer funds from their bank account to another 
    (either internal or external). The transaction is recorded and status updated 
    accordingly. If the sender does not have enough balance or the recipient 
    account cannot be found, an error is displayed.

    Parameters:
    request (HttpRequest): The HTTP request object containing transfer details (recipient account, bank, amount).

    Returns:
    HttpResponse: Redirects to the dashboard with success or error messages.

    Raises:
    ObjectDoesNotExist: If the sender's account or recipient's account does not exist.
    """
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
    """
    Reserve funds for a transaction.

    This view allows the logged-in user to reserve a certain amount of funds 
    without completing a full transaction. The reserved funds are recorded in 
    the Transaction model.

    Parameters:
    request (HttpRequest): The HTTP request object containing the amount to be reserved.

    Returns:
    HttpResponse: Redirects to the 'reserve_success' page upon successful reservation.
    """
    if request.method == 'POST':
        amount = request.POST['amount']

        # Reserve funds logic goes here
        transaction = Transaction(user=request.user, transaction_type='reserve', amount=amount)
        transaction.save()

        return redirect('reserve_success')
    return render(request, 'banking_app/reserve_funds.html')


@login_required
def bank_cards(request):
    """
    Display bank cards associated with the user's account.

    Retrieves the bank cards associated with the logged-in user's bank account 
    and displays them on a separate page.

    Parameters:
    request (HttpRequest): The HTTP request object to fetch the bank cards.

    Returns:
    HttpResponse: Renders a page showing all bank cards associated with the user's account.
    """
    cards = BankCard.objects.filter(user=request.user)
    return render(request, 'banking_app/bank_cards.html', {'cards': cards})


def signup_view(request):
    """
    Handle user sign-up and account creation.

    Renders the sign-up form and creates a new user account and associated 
    bank account upon successful form submission. After creating the account, 
    the user is logged in and redirected to the profile completion page.

    Parameters:
    request (HttpRequest): The HTTP request object containing user sign-up data.

    Returns:
    HttpResponse: Redirects to the profile completion page after successful sign-up.
    """
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
    """
    Handle user login.

    This view authenticates the user based on the provided credentials. 
    Upon successful login, the user is redirected to the dashboard.

    Parameters:
    request (HttpRequest): The HTTP request object containing login data.

    Returns:
    HttpResponse: Redirects to the dashboard upon successful login.
    """
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
    """
    Log the user out.

    Logs the user out of the application and redirects them to the login page.

    Parameters:
    request (HttpRequest): The HTTP request object initiating the logout process.

    Returns:
    HttpResponse: Redirects to the login page after successful logout.
    """
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """
    Display the user's dashboard.

    This view displays the user's account information, associated bank cards, 
    and any relevant error or success messages if the account or cards do not exist.

    Parameters:
    request (HttpRequest): The HTTP request object to fetch user data.

    Returns:
    HttpResponse: Renders the dashboard page with account and card information.
    """
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
    """
    Reveal a user's card details.

    This view allows the logged-in user to view detailed information about a specific 
    card by verifying their PIN.

    Parameters:
    request (HttpRequest): The HTTP request object containing the card ID and user input.
    card_id (int): The ID of the card to be revealed.

    Returns:
    HttpResponse: Renders the card details page if the PIN is verified.
    """
    card = get_object_or_404(Card, id=card_id, user=request.user)
    return render(request, 'banking_app/reveal_card.html', {'card': card})


@login_required
def services(request):
    """
    Display available services (loan and insurance).

    This view displays forms for users to apply for loans or insurance.

    Parameters:
    request (HttpRequest): The HTTP request object to fetch available services.

    Returns:
    HttpResponse: Renders the services page with loan and insurance forms.
    """
    loan_form = LoanForm()
    insurance_form = InsuranceForm()
    return render(request, 'banking_app/services.html', {
        'loan_form': loan_form,
        'insurance_form': insurance_form
    })


@login_required
def support(request):
    """
    Display the support page.

    This view simply renders the support page where users can get assistance.

    Parameters:
    request (HttpRequest): The HTTP request object to load the support page.

    Returns:
    HttpResponse: Renders the support page.
    """
    return render(request, 'banking_app/support.html')


def generate_account_number():
    """
    Generate a random 12-digit account number.

    This helper function generates a random account number used when creating a 
    new bank account for a user.

    Returns:
    str: A 12-digit string representing a unique account number.
    """
    return str(random.randint(100000000000, 199999999999))


def generate_card_number():
    """
    Generate a random 16-digit card number.

    This helper function generates a random card number used when creating a 
    new bank card for a user.

    Returns:
    str: A 16-digit string representing a card number.
    """
    return str(random.randint(4000000000000000, 4999999999999999)) 


def generate_cvv():
    """
    Generate a random 3-digit CVV code.

    This helper function generates a random CVV code used when creating a 
    new bank card for a user.

    Returns:
    str: A 3-digit string representing a CVV code.
    """
    return str(random.randint(100, 999))


@login_required
def complete_profile(request):
    """
    Allow the user to complete their profile.

    This view allows the user to fill in their profile details (like full name) 
    and generate a bank account and card if they do not already have one. 
    An email is sent to the user upon successful profile completion.

    Parameters:
    request (HttpRequest): The HTTP request object containing profile information.

    Returns:
    HttpResponse: Redirects to the dashboard page after profile completion.
    """
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
    """
    Handle loan application.

    This view allows users to apply for a loan by submitting a form. Upon successful 
    form submission, the loan application is saved, and the user is redirected 
    to the loan success page.

    Parameters:
    request (HttpRequest): The HTTP request object containing loan application data.

    Returns:
    HttpResponse: Redirects to the loan success page upon successful application.
    """
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
    """
    Handle insurance application.

    This view allows users to apply for insurance by submitting a form. Upon successful 
    form submission, the insurance application is saved, and the user is redirected 
    to the insurance success page.

    Parameters:
    request (HttpRequest): The HTTP request object containing insurance application data.

    Returns:
    HttpResponse: Redirects to the insurance success page upon successful application.
    """
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
    """
    Display the user's card details after PIN verification.

    This view allows the logged-in user to view their card details. The user must 
    provide their PIN via a POST request. If the entered PIN matches the user's 
    stored PIN, the card details are displayed. If the PIN is incorrect, an error 
    message is shown.

    Parameters:
    request (HttpRequest): The HTTP request object that contains the PIN entered by the user.

    Returns:
    HttpResponse: Renders the card details page with either the card details or an error message.
    
    Raises:
    None
    """
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
    """
    Display loan application success message.

    This view is displayed after the user successfully applies for a loan.

    Parameters:
    request (HttpRequest): The HTTP request object for the loan success page.

    Returns:
    HttpResponse: Renders the loan success page.
    """
    # Add any logic for loan success here if needed
    return render(request, 'banking_app/loan_success.html')


def insurance_success(request):
    """
    Display insurance application success message.

    This view is displayed after the user successfully applies for insurance.

    Parameters:
    request (HttpRequest): The HTTP request object for the insurance success page.

    Returns:
    HttpResponse: Renders the insurance success page.
    """
    return render(request, 'banking_app/insurance_success.html')


@login_required
def reveal_card(request, card_id):
    """
    Reveal a specific card's back details after PIN verification.

    This view allows the logged-in user to view the back details of a specific card 
    identified by its `card_id`. The user must provide their PIN to verify access. 
    Upon correct PIN entry, the card details are revealed. If the PIN is incorrect, 
    an error message is shown.

    Parameters:
    request (HttpRequest): The HTTP request object containing the PIN and card ID.
    card_id (int): The ID of the card to be revealed.

    Returns:
    HttpResponse: Renders the reveal card page with either the card details or an error message.

    Raises:
    None
    """
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
    """
    Verify the user's PIN and allow access to bank account and card details.

    This view handles the verification of a user's PIN to access their bank account 
    and associated bank cards. If the correct PIN is entered, the user's bank cards 
    are displayed, and the PIN attempts counter is reset. If the PIN is incorrect, 
    the number of remaining attempts is shown, and the user is locked out after three 
    failed attempts.

    Parameters:
    request (HttpRequest): The HTTP request object containing the PIN entered by the user.

    Returns:
    HttpResponse: Renders the dashboard with either the bank cards or an error message, 
    depending on the verification result.

    Raises:
    BankAccount.DoesNotExist: If no bank account is associated with the user.
    BankCard.DoesNotExist: If no card is associated with the user's account.
    """
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
