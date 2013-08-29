__author__ = 'yakupadakli'

from django.contrib import admin
from article.models import Article, Category


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title', )

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)