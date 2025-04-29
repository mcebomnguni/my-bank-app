from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('services/', views.services, name='services'),      
    path('support/', views.support, name='support'), 
    path('card/<int:card_id>/reveal/', views.reveal_card, name='reveal_card'), 
    path('complete-profile/', views.complete_profile, name='complete_profile'), 
    path('bank_cards/', views.bank_cards, name='bank_cards'),
    path('apply-for-loan/', views.apply_for_loan, name='apply_for_loan'),
    path('apply-for-insurance/', views.apply_for_insurance, name='apply_for_insurance'),
    path('loan-success/', views.loan_success, name='loan_success'),
    path('insurance-success/', views.insurance_success, name='insurance_success'),
    path('transfer/', views.transfer_funds, name='transfer'),
    path('reserve/', views.reserve_funds, name='reserve'), 
    path('verify_pin/', views.verify_pin, name='verify_pin'),
    path('transfer-funds/', views.transfer_funds, name='transfer_funds'),
    path('reserve-funds/', views.reserve_funds, name='reserve_funds'),
]