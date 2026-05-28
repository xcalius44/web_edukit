from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import TeacherProfile
from courses.models import Course


# -----------------------------
# Existing form (keep it)
# -----------------------------
class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.HiddenInput
    )


# -----------------------------
# New Student Registration Form
# -----------------------------
class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


# -----------------------------
# New Teacher Registration Form
# -----------------------------
class TeacherRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Робочий email")
    full_name = forms.CharField(max_length=100, label="Повне ім'я")
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="Опис / Біографія"
    )
    youtube = forms.URLField(required=False)
    telegram = forms.URLField(required=False)
    linkedin = forms.URLField(required=False)
    website = forms.URLField(required=False) 

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "description", "youtube", "telegram", "linkedin", "website", "password1", "password2")

class TeacherProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = [
            'full_name',
            'description',
            'youtube',
            'telegram',
            'linkedin',
            'website',
        ]
        