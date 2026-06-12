"""
URL configuration for event project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from eventapp.views import *

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth-token/', obtain_auth_token, name='token obatain' ),
    path('', include(router.urls)),
    path('eventview/', EventView.as_view(), name='event-view'),
    path('eventadd/', EventAddView.as_view(), name='event-add'),
    path('event_edit/<int:id>/', EventEditView.as_view(),),
    path('register/', UserView.as_view(), name='customer-register'),
    path('useredit/<int:id>/', UserEditView.as_view(), name='user profle editing'),
    path('alluser/', GetAllUserView.as_view()),
    path('current-user/', CurrentUserView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('fav/<int:id>/', FavouriteEventView.as_view(), name='favourite-event'),
    path('removefav/<int:id>/', RemoveFavEvent.as_view(),),
    path('allfav/', GetFavEvent.as_view(),),
    path('event/<int:id>/', EventDetailView.as_view()),
    path('booking/', BookingView.as_view(), name='booking-view'),

    path('ticket/<int:id>/', DownloadTicket.as_view()),


    path('password-reset/send-otp/', SendPasswordResetOTP.as_view(), name='send-password-reset-otp'),
    path('password-reset/confirm/', VerifyPasswordResetOTP.as_view()),
    path('password-reset/reset/', ResetPasswordView.as_view())
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)