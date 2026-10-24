from django import forms
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','phone','role','password']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','phone','role','is_active']
