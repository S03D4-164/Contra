from django import forms
from .models import *

TIMEOUT_CHOICES = (
    (30, '30s'),
    (60, '1m'),
    (120, '2m'),
    (180, '3m'),
)

class QueryForm(forms.Form):
	input = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
	#referer = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}))
	#proxy = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}))
	user_agent = forms.ModelChoiceField(queryset=UserAgent.objects.all().order_by("name"), required=False)
	timeout = forms.ChoiceField(choices=TIMEOUT_CHOICES)

