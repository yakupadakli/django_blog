import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
# Create your models here.
from article.models import Article


class Comment(models.Model):
    comment = models.TextField(max_length=300)
    email = models.EmailField()
    name = models.CharField(
        max_length=150,
        default="Anonymous"
    )
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(
        'content_type',
        'object_id'
    )
    is_active = models.NullBooleanField(
        default=False,
        editable=False
    )
    pub_date = models.DateTimeField(
        default=datetime.datetime.now(),
        editable=False
    )
    article = models.ForeignKey(
        Article,
        null=True,
        default=False
    )

    def __unicode__(self):
        return self.comment

class Activation(models.Model):
    comment = models.ForeignKey(Comment)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()