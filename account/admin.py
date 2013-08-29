from account.models import UserProfile

__author__ = 'yakupadakli'

from django.contrib import admin

#
# class UserProfileAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("username",)}

admin.site.register(UserProfile)