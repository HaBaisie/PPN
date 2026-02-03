from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    certificate = forms.FileField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'certificate')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        certificate = cleaned_data.get('certificate')
        if user_type in ['policymaker', 'analyst'] and not certificate:
            raise forms.ValidationError("Certificate is required for this role.")
        return cleaned_data
