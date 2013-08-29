    # Create your views here.
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from account import tasks
from comment.models import Activation, Comment
from django.utils.translation import ugettext_lazy as _


def confirm_comment(request, activation_key):
    try:
        activation = get_object_or_404(
            Activation,
            activation_key=activation_key
        )
        comment = get_object_or_404(
            Comment,
            id=activation.comment_id
        )
        if not comment.is_active:
            if tasks.is_key_expires(activation.key_expires):
                c = {
                    "message": _("Your Activation key is expired!"),
                    "send_key_again": True
                }
            else:
                c = {"message": _("Your Comment has been activated...")}
                comment.is_active = True
                # comment.save()
                super(Comment, comment).save()
        else:
            c = {"message": _("Comment is already active.")}
    except User.DoesNotExist:
        raise Http404
    return render(request, "activate.html", c)


# def re_send_activation(request):
#     if request.method == "POST":
#         try:
#             email = request.POST.get("email")
#             user = get_object_or_404(User, email=email)
#             user_profile = get_object_or_404(UserProfile, user=user)
#             activation_key = tasks.generate_activation_key(
#                 user_profile.user.username
#             )
#             key_expires = tasks.generate_key_expires_date()
#             tasks.send_activation_code(activation_key, email)
#             user_profile.activation_key = activation_key
#             user_profile.key_expires = key_expires
#             user_profile.save()
#
#         except User.DoesNotExist:
#             raise Http404
#         return HttpResponseRedirect("/account/login/")
#     else:
#         return HttpResponseRedirect("/")


def register_comment(request):
    pass
