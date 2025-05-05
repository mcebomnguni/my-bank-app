from django.db import models
from django.contrib.auth.models import User


class BankAccount(models.Model):
    """
    Represents a user's bank account.

    Stores account number, current balance, and is linked one-to-one with a User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=12, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"



class BankCard(models.Model):
    """
    Represents a physical or virtual bank card linked to a user's account.

    Includes card type, number, CVV, expiry date, and secure PIN.
    """
    CARD_TYPES = [
        ('Visa', 'Visa'),
        ('MasterCard', 'MasterCard'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiry_date = models.CharField(max_length=5)  # MM/YY
    pin = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.card_type} - {self.card_number[-4:]}"


class ServiceApplication(models.Model):
    """
    Represents a user application for a financial service (loan or insurance).

    Tracks the application status and stores personal and financial details.
    """
    SERVICE_CHOICES = [
        ('home_loan', 'Home Loan'),
        ('car_loan', 'Car Loan'),
        ('home_insurance', 'Home Insurance'),
        ('car_insurance', 'Car Insurance'),
        ('funeral_cover', 'Funeral Cover'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    income = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.user.username}"


class UserProfile(models.Model):
    """
    Stores additional user profile information required for banking services.

    Includes full name, identity verification, contact details, and a PIN.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    citizenship = models.CharField(max_length=100)
    identity_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, default='')
    pin = models.CharField(max_length=6, null=True)

    def __str__(self):
        return self.full_name


class Card(models.Model):
    """
    Represents a general card record for display or reference purposes.

    Stores basic card data like cardholder name, card number, CVV, and account number.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cardholder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    account_number = models.CharField(max_length=12)

    def __str__(self):
        return f"Card {self.card_number} for {self.user.username}"


class Loan(models.Model):
    """
    Represents a loan application submitted by a user.

    Includes loan type, amount, term in years, and application status.
    """
    LOAN_TYPES = [
        ('home', 'Home Loan'),
        ('car', 'Car Loan'),
        ('funeral', 'Funeral Cover'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=10, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_years = models.PositiveIntegerField()
    status = models.CharField(max_length=10, default='Pending')

    def __str__(self):
        return f"{self.get_loan_type_display()} - {self.user.username}"


class Insurance(models.Model):
    """
    Represents an insurance application submitted by a user.

    Includes insurance type, coverage amount, duration, and application status.
    """
    INSURANCE_TYPES = [
        ('home', 'Home Insurance'),
        ('car', 'Car Insurance'),
        ('life', 'Life Insurance'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insurance_type = models.CharField(max_length=10, choices=INSURANCE_TYPES)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_years = models.PositiveIntegerField()
    status = models.CharField(max_length=10, default='Pending')

    def __str__(self):
        return f"{self.get_insurance_type_display()} - {self.user.username}"


class Transaction(models.Model):
    """
    Represents a transaction made by a user.

    Supports fund transfers and fund reservations, tracking source, destination, 
    amount, and status.
    """
    TRANSACTION_TYPES = [
        ('transfer', 'Transfer'),
        ('reserve', 'Reserve'),
    ]
    
    TRANSACTION_STATUS = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

    from_account = models.ForeignKey(
        'banking_app.BankAccount',
        related_name='sent_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    to_account_number = models.CharField(max_length=20, null=True, blank=True)
    to_bank = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='Pending')

    def __str__(self):
        return f"{self.transaction_type} - {self.user.username} - ${self.amount} - {self.status}"
    