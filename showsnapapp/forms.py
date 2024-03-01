from django import forms
from .models import Customer

class SignupForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_id', 'password', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'password': forms.PasswordInput()
        }
