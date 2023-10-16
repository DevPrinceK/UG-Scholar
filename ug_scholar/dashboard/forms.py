from django import forms

from api.models import Profile


class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['thumbnail', 'statistics', ]