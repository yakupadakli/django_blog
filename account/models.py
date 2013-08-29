from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.ForeignKey(User,
                             unique=True,
                             related_name="user")
    picture = models.ImageField(upload_to="profile_pics",
                                blank=True,
                                default="not-found.png",
                                verbose_name=_("Profile Picture")
    )
    url = models.URLField(_("Website"),
                          blank=True,
                          null=True)
    birth_date = models.DateField(_("Birth Date"),
                                  blank=True)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    slug = models.SlugField(
        max_length=120,
        unique=True,
        editable=False,
        default="link-broken"
    )

    def __unicode__(self):
        return self.user.username
