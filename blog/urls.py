# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from blog import settings
from django.conf.urls import patterns, include, url
from blog.views import ArticleListView

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'blog.views.home', name='home'),
                       # url(r'^blog/', include('blog.foo.urls')),

                       # Uncomment the admin/doc line below to
                       # enable admin documentation:
                       # url(r'^admin/doc/',
                       # include('django.contrib.admindocs.urls')),
                       url(r'^ckeditor/', include('ckeditor.urls')),
                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^$', "article.views.index",
                           name="index"),

                       url(r'^user/(?P<pk>\d+)/$', ArticleListView.as_view(),
                           name="article-list"),

                       url(r'^articles/',
                           include('article.urls',
                                   namespace="articles",
                                   app_name="article")),
                       url(r'^accounts/',
                           include('account.urls',
                                   namespace="accounts",
                                   app_name="account")),
                       url(r'^comments/',
                           include('comment.urls',
                                   namespace="comments",
                                   app_name="comment")),
                       url(r'^search/$',
                           "article.views.search",
                           name="search"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^uploads/(?P<path>.*)$',
                                'django.views.static.serve', {
                                    'document_root': settings.MEDIA_ROOT,
                                }),
                            # Here the path must match with 'STATIC_URL' setting
                            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.STATIC_ROOT,
                                }),

                            )

handler404 = 'blog.views.handler404'
handler500 = 'blog.views.handler500'
# handler500 = views.handler_500
