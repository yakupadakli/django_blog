__author__ = 'yakupadakli'

from blog import settings
from django.conf.urls import patterns, url
from account import views


urlpatterns = patterns('',
                       url(r'^profile/$',
                           'account.views.profile',
                           name="profile"),
                       url(r'^profile/change-password/$',
                           'account.views.change_password',
                           name="change_password"),

                       #user auth urls
                       url(r'^login/$',
                           'account.views.login',
                           name="login"),
                       url(r'^auth/$',
                           'account.views.login_auth',
                           name="auth"),
                       url(r'^logout/$',
                           'account.views.logout',
                           name="logout"),
                       url(r'^register/$',
                           'account.views.register_user',
                           name="register"),
                       url(r'^re_send_activation/$',
                           views.re_send_activation,
                           name="re_send_activation"),
                       url(r'activate/(?P<activation_key>[-A-Za-z0-9_]+)/$',
                           views.confirm_user,
                           name="confirm_user"),
)
#
if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^uploads/(?P<path>.*)$',
                                'django.views.static.serve', {
                                    'document_root': settings.MEDIA_ROOT,
                                }),
    )