from django import forms

from .models import *

TIMEOUT_CHOICES = (
    (60, '1m'),
    (120, '2m'),
    (180, '3m'),
)

METHOD_CHOICES = (
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('HEAD', 'HEAD'),
)

class QueryForm(forms.Form):
	input = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
	user_agent = forms.ModelChoiceField(queryset=UserAgent.objects.all().order_by("name"), required=False)
	referer = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
	proxy = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
	additional_headers = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
	method = forms.ChoiceField(choices=METHOD_CHOICES)
	post_data = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
	timeout = forms.ChoiceField(choices=TIMEOUT_CHOICES)

class UserAgentForm(forms.ModelForm):
	class Meta:
        	model = UserAgent
        	fields = ['name', 'strings']
	def __init__(self, *args, **kwargs):
        	super(UserAgentForm, self).__init__(*args, **kwargs)
	        self.fields['name'].widget.attrs['style'] = 'width:30%;'
	        self.fields['strings'].widget.attrs['style'] = 'width:30%;'

