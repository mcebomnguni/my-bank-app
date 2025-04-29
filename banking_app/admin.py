from django.contrib import admin
from .models import BankAccount, BankCard
from .models import ServiceApplication
from .models import Card

admin.site.register(Card)
admin.site.register(BankAccount)
admin.site.register(BankCard)
admin.site.register(ServiceApplication)
