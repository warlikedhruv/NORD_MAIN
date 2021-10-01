from django import forms
from users.models import *
from django.utils.translation import ugettext_lazy as _
from .models import *
from django.forms.utils import ErrorList
from questions.models import *
from languages.models import *
from django.contrib.auth.forms import PasswordResetForm
import datetime




ORG_SIZE_CHOICES=[
        ('0 - 10', '0 - 10'),
        ('10 - 50', '10 -50'),
        ('50 - 200','50 - 200'),
        ('200 - 500','200 - 500'),
        ('500+','500+'),
]

class CreateOrganizationForm(forms.ModelForm):
    organisation_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'organisation_name', 'placeholder': 'Organisation Name'}),
        max_length=100, required=True)
    website_url = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'website_url', 'placeholder': 'Website Url'}),
        max_length=200, required=True)
    organization_logo = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'form-control','multiple': False, 'name': 'organization_logo'}),required=False)
    organization_address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'organization_address', 'placeholder': 'Organization Address'}),
        max_length=100, required=True)
    organisation_size = forms.ChoiceField(choices=ORG_SIZE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'organisation_size'}), required=True)

    class Meta:
        model = Tenant
        fields = ['organisation_name','website_url','organization_logo','organization_address','organisation_size']


    def clean_domain(self):
        try:
            domain_name = Tenant.objects.get(website_url__iexact=self.cleaned_data['website_url'])
        except Tenant.DoesNotExist:
            return self.cleaned_data['website_url']
        raise forms.ValidationError(_("The domain name already exists."))



class OrganizationUpadateForm(forms.ModelForm):

    class Meta:
        model = Tenant
        fields = ['organisation_name','website_url','organization_logo','organization_address','organisation_size']

