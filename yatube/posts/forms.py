from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group','image')
        label = {
            'text': ('Текст'),
            'group': ('Группа'),
        }
        help_texts = {
            'text': ('Содержание публицации'),
            'group': ('Принадлежность к группе'),
        }



    def validate_not_empty(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError(
                'А кто поле будет заполнять, Пушкин?',
                params={'data': data},
            )
        return data
