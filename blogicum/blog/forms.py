from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image',
        )
        widgets = {
            'pub_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),
            'created_at': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data['title']
        return name


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )
        fields = {'text', }


User = get_user_model()


class UserRegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )

    def clean_username(self):
        username = self.cleaned_data['username'].lower()

        forbidden = ('admin', 'edit', 'root', 'superuser')

        if username in forbidden:
            raise ValidationError(f'Запрещено имя: {username}')
        
        return username
