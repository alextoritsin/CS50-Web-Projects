# from .models import Bid
from django import forms

class AddListing(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={
                                'class': 'form-control',
                                'autofocus': 'autofocus',
                            }))
    category = forms.CharField(label="Category", widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                               }))
    starting_bid = forms.DecimalField(label="Starting Bid", min_value=0.01,
                                      max_digits=8, decimal_places=2,
                                      widget=forms.NumberInput(attrs={
                                          'class': 'form-control',
                                      }))
    url = forms.URLField(required=False, label="URL for Image", widget=forms.URLInput(attrs={
                             'class': 'form-control',
                         }))

    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={
                                      'class': 'form-control',
                                  }))



class BidForm(forms.Form):
    last_bid = forms.DecimalField(min_value=0.01, max_digits=8, decimal_places=2,
                             widget=forms.NumberInput(attrs={
                                'class': 'form-control',
                            }))


