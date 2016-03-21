from django import forms
from django.contrib.auth.models import User, Group

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

class InputForm(forms.Form):
    input = forms.CharField(max_length=200)

class DNSForm(forms.Form):
    query = forms.CharField(max_length=200)
    resolver = forms.CharField(max_length=200, required=False)

header = "Accept-Language: ja; q=1.0, en; q=0.5"
#Accept: text/html; q=1.0, text/*; q=0.8, image/gif; q=0.6, image/jpeg; q=0.6, image/*; q=0.5, */*; q=0.1

class QueryForm(forms.Form):
    input = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), initial="http://")
    user_agent = forms.ModelChoiceField(queryset=UserAgent.objects.all().order_by("name"), required=False, initial=1)
    referer = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
    proxy = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40, 'placeholder':"http://ipaddress:port"}), required=False)
    additional_headers = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False, initial=header)
    method = forms.ChoiceField(choices=METHOD_CHOICES)
    post_data = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
    timeout = forms.ChoiceField(choices=TIMEOUT_CHOICES, initial=180)

class QueryRunForm(forms.Form):
    user_agent = forms.ModelChoiceField(queryset=UserAgent.objects.all().order_by("name"), required=False, initial=1)
    referer = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
    proxy = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40, 'placeholder':"http://ipaddress:port"}), required=False)
    additional_headers = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False, initial=header)
    method = forms.ChoiceField(choices=METHOD_CHOICES)
    post_data = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
    timeout = forms.ChoiceField(choices=TIMEOUT_CHOICES, initial=180)

class UserAgentForm(forms.ModelForm):
    class Meta:
        model = UserAgent
        fields = ['name', 'strings']
    def __init__(self, *args, **kwargs):
        super(UserAgentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['style'] = 'width:30%;'
        self.fields['strings'].widget.attrs['style'] = 'width:30%;'

class DomainConfigForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ['whitelisted']

INTERVAL_CHOICES = (
    (0, 'disable'),
    (1800, '30m'),
    (3600, '1h'),
    (10800, '3h'),
    (21600, '6h'),
)

RESTRICTION_CHOICES = (
    (0, 'login_user'),
    (1, 'group_only'),
    (2, 'all_user'),
)

class QueryConfigForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['restriction', 'interval', 'counter']
    def __init__(self, *args, **kwargs):
        super(QueryConfigForm, self).__init__(*args, **kwargs)
        self.fields['interval'].widget = forms.Select(choices=INTERVAL_CHOICES)
        self.fields['restriction'].widget = forms.Select(choices=RESTRICTION_CHOICES)

class SearchForm(forms.Form):
    url = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
    ip = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
    payload = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size': 40}), required=False)
    webapp = forms.ModelMultipleChoiceField(queryset=Webapp.objects.all().order_by("name"), required=False)
    date_from = forms.DateTimeField(required=False)
    date_to = forms.DateTimeField(required=False)
    signature = forms.ModelMultipleChoiceField(queryset=YaraRule.objects.all().order_by("name"), required=False)
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['webapp'].widget.attrs['style'] = 'height:100px;width:30%;'

class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

