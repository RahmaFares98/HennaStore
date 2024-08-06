from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['Comment', 'Rating']
        widgets = {
            'Comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
            'Rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)])
        }
