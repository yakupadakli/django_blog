from django import forms
from comment.models import Comment

__author__ = 'yakupadakli'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', "email", 'comment', )