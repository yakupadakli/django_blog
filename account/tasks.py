__author__ = 'yakupadakli'

import datetime
from django.contrib.sites.models import Site
import pytz
from random import random
# import hashlib
from django.utils.hashcompat import sha_constructor
from celery.task import task
from django.utils.translation import ugettext_lazy as _
from blog.settings import EXPIRES_DATE


def mail_sending(activation_key, purpose, to_email, subject):
    from django.core.mail import send_mail
    link = generate_link(activation_key, purpose)
    message_new = _("Your Activation link is : ") + str(link)
    send_mail(subject, message_new,
              'yakup.adakli@markafoni.com',
              [to_email], fail_silently=False)


@task(ignore_result=True)
def send_activation_code(activation_key,
                         to_email,
                         purpose="user_activation"):
    """
    Send an email when user register and comment are added
    """

    if purpose == "user_activation":
        mail_sending(activation_key, purpose,
                     to_email, _('E-mail Activation Code'))
    else:
        mail_sending(activation_key, purpose,
                     to_email, _('Comment Activation Code'))


def generate_activation_key(user):
    """
        Generate activation key
    :param user:
    :return:
    """
    salt = sha_constructor(str(random()) + user).hexdigest()[:20]
    return salt


def generate_key_expires_date():
    """
        Generate key expires date for activation keys
    :return:
    """
    key_expires = datetime.datetime.today() + datetime.timedelta(
        EXPIRES_DATE
    )
    return key_expires


def generate_link(activation_key, purpose="user_activation"):
    """
        Generate link for user activation or comment activation
    :param activation_key: activation key which is for
        user activation or comment activation
    :param purpose: gives activation is for what
    :return:
    """
    if purpose == "user_activation":
        link = Site.objects.get_current() + "accounts/activate/"+str(
            activation_key)
    else:
        link = Site.objects.get_current() + "comments/activate/"+str(
            activation_key)
    return link


def is_key_expires(key_expires_date):
    """
        Looking key`s key expires date finished or not
    :param key_expires_date:
    :return:
    """
    if key_expires_date <= datetime.datetime.utcnow().replace(
            tzinfo=pytz.utc):
        return True
    else:
        return False


@task(ignore_result=True)
@task(name='resize-image')
def resize_image(image, max_height=170, max_width=140):
    """
        Re-sizing given image with a ratio of
        given width and height
    :param image:
    :param max_height: max height of product image
    :param max_width: max width of product image
    """
    from PIL import Image
    import os

    _parent = lambda x: os.path.normpath(os.path.join(x, '..'))
    PROJECT_DIR = _parent(os.path.dirname(__file__))
    new_image = Image.open(os.path.join(PROJECT_DIR, 'uploads/' + str(
        image)))
    new_image.thumbnail((max_height, max_width), Image.ANTIALIAS)
    new_image.save(os.path.join(PROJECT_DIR, 'uploads/' + str(image)))