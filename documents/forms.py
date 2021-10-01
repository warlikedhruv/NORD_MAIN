from django import forms
from .models import Document,PrivateAccess
from organisations.models import Tenant

file_type = [
    ('public', 'public'),
    ('private', 'private')
]

class DocumentForm(forms.ModelForm):
    document_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'document_name', 'placeholder': 'File Name'}),
        max_length=50, required=True)
    document_description = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'document_description', 'placeholder': 'Description'}),
        max_length=50, required=True)
    doc_type = forms.ChoiceField(choices=file_type, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'doc_type'}), required=True)
    document = forms.FileField(label='Select a file')

 
    class Meta:
        model = Document
        fields = ['document_name','document_description','doc_type','document']   


class DocumentAccessForm(forms.ModelForm):
    all_organzations = Tenant.objects.all().order_by('id')
    tenant = forms.ModelChoiceField(queryset=all_organzations, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'tenant'}), required=True)

    class Meta:
        model = PrivateAccess
        fields = ['access_tenant']

