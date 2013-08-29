from random import choice
from string import letters
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from account import tasks
from account.decorators import anonymous_required
from account.forms import UserProfileForm, \
    UserRegisterForm, \
    UserForm, \
    ChangePasswordForm
from account.models import UserProfile
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

__author__ = 'yakupadakli'


@login_required(login_url='/accounts/login/')
def profile(request):
    """
        This view show user`s profile page and it allows the users
        update their profiles
        Works of this view mainly if request method is "POST", it takes
        all data and looks they are valid or not if form is valid
        data are saving the table which are user_profile and user
        in the database

    :param request:
    :return:
        it returns profile page with users information
    """
    # try:
    user_profile = request.user.get_profile()
    if request.method == "POST":
        data = request.POST.copy()
        new_user_form = UserForm(data)
        new_user_profile_form = UserProfileForm(data)
        # checking form validation
        if new_user_form.is_valid() and new_user_profile_form.is_valid():
            picture = request.FILES.get("picture")

            # checking email change or not
            # if email was changed, new activation
            # code will send the new email address
            if user_profile.user.email != data["email"]:
                activation_key = tasks.generate_activation_key(
                    user_profile.user.username
                )
                key_expires_date = tasks.generate_key_expires_date()
                tasks.send_activation_code.delay(
                    activation_key,
                    data["email"]
                )
                user_profile.key_expires = key_expires_date
                user_profile.activation_key = activation_key
                user_profile.user.is_active = False
                user_profile.user.email = data["email"]

            user_profile.user.first_name = data["first_name"]
            user_profile.user.last_name = data["last_name"]
            user_profile.birth_date = data["birth_date"]
            user_profile.url = data["url"]

            # checking picture if it is not empty
            # delete previous one
            if picture is not None:
                if picture is not "not-found.png":
                    user_profile.picture.delete(save=False)
                user_profile.picture = picture

            # saving new user profile and this profile`s user
            user_profile.save()
            user_profile.user.save()

            # determining success message
            messages.success(
                request,
                _('Profile details updated successfully.'),
                fail_silently=True
            )

            # if profile saves successfully,
            # profile picture resizing with pil by using celery task
            if picture is not None:
                tasks.resize_image.delay(user_profile.picture, 240, 240)

            # sending form to template with initial data
            # because i do not send any extra data to view
            # it needs first data
            new_user_form = UserForm(initial={
                "email": user_profile.user.email,
                "username": user_profile.user.username,
                "first_name": user_profile.user.first_name,
                "last_name": user_profile.user.last_name}
            )

            new_user_profile_form = UserProfileForm(initial={
                "picture": user_profile.picture,
                "url": user_profile.url,
                "birth_date": user_profile.birth_date}
            )
        else:
            user_profile = request.user.get_profile()
            # determining error message
            messages.error(
                request,
                _('Profile details failed.'),
                fail_silently=True
            )

            new_user_form = UserForm(data)
            new_user_profile_form = UserProfileForm(data)
    else:
        user_profile = request.user.get_profile()
        # user_profile = UserProfile.objects.get(slug=slug)
        new_user_form = UserForm(initial={
            "email": user_profile.user.email,
            "username": user_profile.user.username,
            "first_name": user_profile.user.first_name,
            "last_name": user_profile.user.last_name}
        )

        new_user_profile_form = UserProfileForm(initial={
            "picture": user_profile.picture,
            "url": user_profile.url,
            "birth_date": user_profile.birth_date}
        )

    c = {"user_profile": user_profile,
         "user_profile_form": new_user_profile_form,
         "user_form": new_user_form}

    if user_profile is not None:
        return render(request, "profile.html", c)
    else:
        return redirect(reverse('index'))
        # except:
        #     raise Http404


@anonymous_required(redirect_url="/accounts/profile")
def login(request):
    return render(request, "login.html")


def login_auth(request):
    """
        This view allow the users login and check their login details
        are correct or not
    :param request:
    :return: :raise:
        If login success, users will direct to profile page
        If not, it gives error
    """

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(
        username=username,
        password=password
    )

    if user is not None:
        if user.is_active:
            # if user exist and is active, login will successful
            auth.login(request, user)
            messages.success(
                request,
                _('Login successful.'),
                fail_silently=True
            )
            return redirect(reverse("accounts:profile"))
        else:
            return render(
                request,
                "login.html",
                {"fail": True, "is_active": False}
            )
    else:
        return render(
            request,
            "login.html",
            {"fail": True, "is_active": True}
        )


@login_required(login_url='/accounts/login/')
def logout(request):
    """
        Logout the users
    :param request:
    :return:
        Return homepage
    """
    auth.logout(request)
    messages.success(
        request,
        _('Logout successful.'),
        fail_silently=True
    )
    return redirect(reverse("index"))
    # return render(request, "logout.html")


@anonymous_required(redirect_url="/accounts/profile")
def register_user(request):
    """
        User sign up form

    :param request:
    """
    if request.method == "POST":
        data = request.POST.copy()
        data['username'] = ''.join([choice(letters) for i in xrange(30)])
        user_register_form = UserRegisterForm(data)
        if user_register_form.is_valid():
            # creating activation code for new user
            activation_key = tasks.generate_activation_key(
                data["username"]
            )
            # creating expired date for new activation key
            key_expires = tasks.generate_key_expires_date()
            tasks.send_activation_code.delay(
                activation_key,
                data["email"]
            )

            user_register_form.save()

            user = User.objects.get(username=data['username'])
            url = data["url"]
            birth_date = data["birth_date"]
            user_profile = UserProfile(user=user,
                                       url=url,
                                       birth_date=birth_date,
                                       activation_key=activation_key,
                                       key_expires=key_expires)
            user_profile.save()
            messages.success(
                request,
                _('Registration successful. You need to confirm your account.'),
                fail_silently=True
            )
            return render(request, "login.html")
    else:
        user_register_form = UserRegisterForm()
    c = {"form": user_register_form}
    c.update(csrf(request))
    return render(request, "register.html", c)


def confirm_user(request, activation_key):
    """
        When users register to the site,
        they need to be confirm their email address
        This view help to check confirmation code is right or not
        if code is expired send a new code
    :param request:
    :param activation_key: code for activating tho user
    :return: :raise:

    """
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if not user_profile.user.is_active:
        if tasks.is_key_expires(user_profile.key_expires):
            c = {
                "message": _("Your Activation key is expired!"),
                "send_key_again": True
            }
        else:
            c = {"message": _("Your Account has been activated...")}
            user_profile.user.is_active = True
            user_profile.user.save()
    else:
        c = {"message": _("User is already active.")}
    return render(request, "activate.html", c)


def re_send_activation(request):
    """
        When activation code is expired, this function send it again
    :param request:
    :return: :raise:
    """
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            user = get_object_or_404(User, email=email)
            user_profile = get_object_or_404(UserProfile, user=user)
            # creating activation key again
            activation_key = tasks.generate_activation_key(
                user_profile.user.username
            )
            key_expires = tasks.generate_key_expires_date()
            tasks.send_activation_code(activation_key, email)
            user_profile.activation_key = activation_key
            user_profile.key_expires = key_expires
            user_profile.save()
            messages.success(
                request,
                _('Activation code sent successfully.'),
                fail_silently=True
            )
        except User.DoesNotExist:
            raise Http404
        return redirect(reverse("accounts:login"))
    else:
        return redirect(reverse("index"))


@login_required(login_url='/accounts/login/')
def change_password(request):
    """
        Password changing
    :param request:
    :return:
    """
    user = request.user.get_profile()
    if request.method == "POST":
        data = request.POST.copy()
        change_password_form = ChangePasswordForm(user.user, data)
        if change_password_form.is_valid():
            change_password_form.save()
            messages.success(
                request,
                _('Password changed successfully.'),
                fail_silently=True
            )
            return redirect(reverse("profile"))
        else:
            change_password_form = ChangePasswordForm(user.user, data)
    else:
        change_password_form = ChangePasswordForm(user.user)
    c = {"form": change_password_form}
    return render(request, "change_password.html", c)