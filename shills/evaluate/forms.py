from django import forms

class SearchForm(forms.Form):
    title = forms.CharField(label='Movie:', max_length=100)
