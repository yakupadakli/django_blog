from blog import settings

__author__ = 'yakupadakli'

from django.conf.urls import patterns, url
from comment import views


urlpatterns = patterns('',
                       url(r'^register/$',
                           'comment.views.register_comment',
                           name='register_comment'),
                       # url(r'^re_send_activation/$',
                       #     views.re_send_activation,
                       #     name="re_send_activation"),
                       url(r'activate/(?P<activation_key>[-A-Za-z0-9_]+)/$',
                           views.confirm_comment,
                           name="confirm_comment"),)


if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^uploads/(?P<path>.*)$',
                                'django.views.static.serve',
                                {
                                    'document_root': settings.MEDIA_ROOT,
                                }
                            ),
    )