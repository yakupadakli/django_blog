from django import forms
from article.models import Article
from django.utils.translation import ugettext_lazy as _
__author__ = 'yakupadakli'


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title',
                  "body",
                  'image',
                  'categories',
                  'tags',
                  'author')
        labels = {
            'title': _("Title Add"),
            'image': _('Highlight image'),
        }
        widgets = {
            "title": forms.TextInput(attrs={
                'title': _("Please provide a title."),
                "class": "form-control"}),
            "categories": forms.SelectMultiple(attrs={
                'title': _("Please select categories."),
                "class": "form-control"}),
            "tags": forms.TextInput(attrs={
                'title': _("Please provide tags."),
                "class": "form-control"}),
            "author": forms.HiddenInput()
            # "slug": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['image'].label =_("Highlight image")