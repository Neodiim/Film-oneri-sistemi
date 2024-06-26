from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
    password = forms.CharField(label="Şifre",widget=forms.PasswordInput)
    email=forms.CharField(widget=forms.EmailInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Kullanıcı Adı',
            'email': 'E-posta',
         
        }
