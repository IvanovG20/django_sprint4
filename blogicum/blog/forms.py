from django import forms
from django.core.mail import send_mail

from blogicum.settings import EMAIL_CONST

from .models import Comment, Post


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

    def clean(self):
        super().clean()
        send_mail(
            subject='Comment',
            message='Вы оставили коментарий!',
            from_email=EMAIL_CONST,
            recipient_list=['admin@blogicum.not'],
            fail_silently=True,
        )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }
