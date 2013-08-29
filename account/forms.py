
from django.contrib.auth.models import User
from django import forms
from account.models import UserProfile
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import ugettext_lazy as _

__author__ = 'yakupadakli'


class UserForm(forms.ModelForm):
    """
        Form form User table in database
    :param args:
    :param kwargs:
    """
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'title': _("Please provide your email address."),
                "class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', "username", "email"]

        widgets = {
            "first_name": forms.TextInput(
                attrs={'title': _("Please provide your first name."),
                       "class": "form-control"}),
            "last_name": forms.TextInput(
                attrs={'title': _("Please provide your last name."),
                       "class": "form-control"}),
            "username": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):

        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = _("First Name")
        self.fields['last_name'].label = _("Last Name")
        self.fields.keyOrder = [
            'email',
            'username',
            'first_name',
            'last_name']

    def clean(self):
        data = self.cleaned_data.copy()
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(
                email=email
        ).exclude(
                username=username
        ).count():
            raise forms.ValidationError(_(
                "Email address already exists."))
        return data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['picture', 'url', 'birth_date']

        widgets = {
            "url": forms.TextInput(
                attrs={'title': _("Please provide your website."),
                       "class": "form-control"}),
            "birth_date": forms.TextInput(
                attrs={'title': _("Please provide your birth date."),
                       "class": "form-control",
                       "id": "datepicker"}),
        }


class ChangePasswordForm(PasswordChangeForm):

    old_password = forms.CharField(
        max_length=75,
        widget=forms.PasswordInput(attrs={
            'title': _("Please provide your old password."),
            "class": "form-control"}))
    new_password1 = forms.CharField(
        label=_("New password"),
        max_length=75,
        widget=forms.PasswordInput(attrs={
            'title': _("Please provide your new password."),
            "class": "form-control"}))
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        max_length=75,
        widget=forms.PasswordInput(attrs={
            'title': _("Please provide your new password confirmation."),
            "class": "form-control"}))


class UserRegisterForm(UserCreationForm):
    """ Require email address when a user signs up """
    email = forms.EmailField(
        label=_('Email address'),
        max_length=75,
        widget=forms.TextInput(
            attrs={
                'title': _("Please provide your email address."),
                "class": "form-control"}))

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                'title': _("Please provide your password."),
                "class": "form-control"}))
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={
                'title': _("Please provide your password confirmation."),
                "class": "form-control"}))
    url = forms.URLField(
        label=_("Website"),
        required=False,
        widget=forms.TextInput(attrs={
            'title': _("Please provide your website."),
            "class": "form-control"}))
    # picture = forms.ImageField(label="Profile Picture")
    birth_date = forms.DateField(
        label=_("Birth Date"),
        required=True,
        widget=forms.TextInput(
            attrs={
                'title': _("Please provide your birth date."),
                "id": "datepicker",
                "class": "form-control"}))

    class Meta:
        model = User
        fields = ('username', "email", 'first_name', 'last_name', )

        widgets = {
            "first_name": forms.TextInput(
                attrs={'title': _("Please provide your first name."),
                       "class": "form-control"}),

            "last_name": forms.TextInput(
                attrs={'title': _("Please provide your last name."),
                       "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = _("First Name")
        self.fields['last_name'].label = _("Last Name")
        self.fields.keyOrder = [
            'username',
            'email',
            'password1',
            'password2',
            'birth_date',
            'first_name',
            'last_name',
            'url']

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            raise forms.ValidationError(_(
                "This email address already exists. "
                "Did you forget your password?"))
        except User.DoesNotExist:
            return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        user.is_active = False  # change to false if using email activation
        if commit:
            user.save()
        return user