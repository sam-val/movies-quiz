from user.models import MyUser
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext as _

class SignupForm(forms.ModelForm):
    re_password = forms.CharField(max_length=255, required=True, widget=forms.PasswordInput, validators=[])
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'password', 're_password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_re_password(self):
        re_password = self.cleaned_data['re_password']
        password = self.cleaned_data['password']

        if re_password != password:
            raise ValidationError(_("Password did not match."), code='invalid')
        
        return re_password

class MyAuthenticationForm(AuthenticationForm):
    pass


