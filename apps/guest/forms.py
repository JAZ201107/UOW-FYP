from django import forms
from apps.guest.models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = (
            'image',
            'caption',
        )
