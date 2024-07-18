from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'tag', 'region', 'travel_start_date', 'travel_end_date']
        widgets = {
            'tag': forms.CheckboxSelectMultiple(),
        }