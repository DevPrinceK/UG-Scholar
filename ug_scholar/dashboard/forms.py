from django import forms

from api.models import Profile


class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "name",
            "scholar_id",
            "orcid",
            "source_author_id",
            "affiliation",
            "rank",
            "email",
            "college",
            "school",
            "department",
        ]
