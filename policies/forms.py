from django import forms
from .models import Policy, Comment


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ('name', 'description')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
