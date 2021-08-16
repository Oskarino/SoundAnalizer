from django import forms
from django.core.validators import ValidationError
from django.contrib.auth.models import User

class UploadAudioForm(forms.Form):
    audio_file = forms.FileField()

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20, label="Nazwa użytkownika:")
    first_name = forms.CharField(max_length=20, label="Imię:")
    last_name = forms.CharField(max_length=20, label="Nazwisko:")
    password = forms.CharField(max_length=32, widget=forms.PasswordInput, label="Hasło:")
    password2 = forms.CharField(max_length=32, widget=forms.PasswordInput, label="Powtórz Hasło:")
    email =  forms.EmailField(label="E-mail:")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Nazwa użytkownika jest zajęta")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Masz juz konto z tym e-mailem")
        return email

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                raise ValidationError("Hasła są od siebie różne")

    def save(self):
        User.objects.create_user(username=self.cleaned_data['username'],
                                 password=self.cleaned_data['password'],
                                 email=self.cleaned_data['email'],
                                 first_name=self.cleaned_data['first_name'],
                                 last_name=self.cleaned_data['last_name'])

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label="Nazwa użytkownika:")
    password = forms.CharField(max_length=32, widget=forms.PasswordInput, label="Hasło:")
    user = None

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if password and username:
            user = User.objects.filter(username__iexact=username).first()
            if user is not None and user.check_password(password):
                self.user = user
                return
        raise ValidationError("Zły login lub hasło.")
