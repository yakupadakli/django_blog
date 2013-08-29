__author__ = 'yakupadakli'
from comment.models import Comment
from django.contrib import admin

#
# class UserProfileAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("username",)}

admin.site.register(Comment)