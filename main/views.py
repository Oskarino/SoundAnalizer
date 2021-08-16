from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import FormView, View, ListView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from main.models import Audio
from main.audio import process_user_file
from main.forms import UploadAudioForm, RegistrationForm, LoginForm


# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html', {'token': get_token(request)})



@login_required
def upload_audio(request):
    form = UploadAudioForm(request.POST, request.FILES)
    if form.is_valid():
        file = form.cleaned_data['audio_file']
        process_user_file(file, request.user)
        #print(analyze(file_name))
        messages.add_message(request, messages.INFO, 'Twój plik został wgrany')
        return HttpResponse()
    else:
        return HttpResponse(status=400)


@method_decorator(login_required, name='dispatch')
class DeleteAudioView(DeleteView):
    model = Audio
    template_name = 'audio_confirm_delete.html'
    success_url = reverse_lazy('audio_listing')

    def get_object(self, queryset=None):
        audio = super().get_object(queryset)
        if audio.user_id == self.request.user.id:
            return audio
        raise PermissionDenied()

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.add_message(self.request, messages.ERROR, 'Pomyślnie usunięto plik')
        return response

class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        form.save()
        #uruchom domyslne zakonczenie form_valid,
        #tutaj django wykona przekierowanie
        messages.add_message(self.request, messages.SUCCESS, 'Zarejstrowano pomyślnie')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('index')


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        #user = form.get_user()
        login(self.request,form.user)
        messages.add_message(self.request, messages.SUCCESS, 'Zalogowano pomyślnie')
        #uruchom domyslne zakonczenie form_valid,
        #tutaj django wykona przekierowanie
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('index')

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.add_message(self.request, messages.WARNING, 'Wylogowano pomyślnie')
        return redirect(reverse('index'))


@method_decorator(login_required, name='dispatch')
class AudioListingView(ListView):
    template_name = 'audio_listing.html'
    #queryset = Audio.objects.order_by('-created_at')
    def get_queryset(self):
        return Audio.objects.filter(user=self.request.user).order_by('-created_at')

