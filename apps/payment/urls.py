                      
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
                  
    path('create-checkout-session/', 
         views.CreateCheckoutSessionView.as_view(), 
         name='create_checkout_session'),
    
    path('success/', 
         views.PaymentSuccessView.as_view(), 
         name='payment_success'),
    
    path('canceled/', 
         views.PaymentCanceledView.as_view(), 
         name='payment_canceled'),
    
                    
    path('webhook/', 
         views.StripeWebhookView.as_view(), 
         name='stripe_webhook'),
    
                     
    path('history/', 
         views.PaymentHistoryView.as_view(), 
         name='payment_history'),
    
    path('detail/<int:pk>/', 
         views.PaymentDetailView.as_view(), 
         name='payment_detail'),
]
