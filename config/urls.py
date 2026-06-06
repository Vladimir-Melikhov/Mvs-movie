from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import PrivacyPolicyView                    

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('ratings/', include('apps.ratings.urls', namespace='ratings')),
    path('player/', include('apps.player.urls', namespace='player')),
    path('payment/', include('apps.payment.urls', namespace='payment')),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('', include('apps.movies.urls', namespace='movies')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)