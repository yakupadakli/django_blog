__author__ = 'yakupadakli'

from blog import settings
from django.conf.urls import patterns, url


urlpatterns = patterns('',

                       url(r'^add-article/$',
                           'article.views.add_article',
                           name='add_article'),
                       url(r'^my-articles/$',
                           'article.views.my_article',
                           name='my_article'),
                       url(r'edit/(?P<slug>[-A-Za-z0-9_]+)/$',
                           "article.views.edit_article",
                           name='edit_article'),
                       url(r'(?P<slug>[-A-Za-z0-9_]+)/$',
                           "article.views.detail",
                           name='detail'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^uploads/(?P<path>.*)$',
                                'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT,
                            }),
    )