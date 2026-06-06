                       
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
                         
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('registration-complete/', views.registration_complete, name='registration_complete'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<str:token>/',
             views.CustomPasswordResetConfirmView.as_view(),
             name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('settings/', views.UserProfileUpdateView.as_view(), name='settings'),
]