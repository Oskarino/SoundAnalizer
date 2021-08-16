"""SoundAnalizer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from main.views import index, upload_audio, RegistrationView, LoginView, LogoutView, AudioListingView, DeleteAudioView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('upload-audio', upload_audio, name='upload_audio'),
    path('rejestracja', RegistrationView.as_view(), name='registration'),
    path('logowanie', LoginView.as_view(), name='login'),
    path('wylogowanie', LogoutView.as_view(), name='logout'),
    path('lista', AudioListingView.as_view(), name='audio_listing'),
    path('usuwanie/<int:pk>', DeleteAudioView.as_view(), name='audio_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
