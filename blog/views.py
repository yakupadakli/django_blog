import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.views.generic import DetailView
from django.contrib.auth.models import User


def handler404(request):
    response = render(
        request, '404.html')
    response.status_code = 404
    return response


def handler500(request):
    response = render(
        request, '500.html'
    )
    response.status_code = 500
    return response


class JSONResponseMixin(object):
    SERIALIZER = serializers.get_serializer("json")()
    serializable_keys = []
    serialization_fields = []

    def render_to_response(self, context):
        result = {}
        for key, value in context.iteritems():
            if key in self.serializable_keys:
                result[key] = self.SERIALIZER.serialize(value, fields=self.serialization_fields)
        return HttpResponse(json.dumps(result), 'application/json')


class ArticleListView(DetailView, JSONResponseMixin):
    queryset = User.objects.all()
    template_name = 'article_list.html'
    serializable_keys = ['object_list']
    serialization_fields = ['title', 'author']

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = self.object.author.all()
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['message'] = 'Hello World'
        return context

    def render_to_response(self, context):
        if 'ajax' in self.request.GET:
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return DetailView.render_to_response(self, context)
