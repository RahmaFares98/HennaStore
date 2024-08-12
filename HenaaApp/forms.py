# use django forms
from django import forms
from .models import *

class ReviewForm(forms.ModelForm): #ModelForm: Inherits from forms.ModelForm
    #the Meta class provides options for controlling things like database table names, ordering, verbose names
    class Meta:
        model = Review
        fields = ['Comment', 'Rating']
        widgets = {
            'Comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
            'Rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)])
        }


class PaymentForm(forms.Form):
    name_on_card = forms.CharField(max_length=100, required=True)
    card_number = forms.CharField(max_length=16, required=True, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    expiration_date = forms.CharField(max_length=5, required=True, widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    cvv = forms.CharField(max_length=3, required=True, widget=forms.TextInput(attrs={'placeholder': 'CVV'}))
    stripe_token = forms.CharField(widget=forms.HiddenInput)  # Assuming you're using Stripe
