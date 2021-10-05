from django import forms
from users.models import *
from django.utils.translation import ugettext_lazy as _
from organisations.models import *
from django.forms.utils import ErrorList
from questions.models import *
from languages.models import *
from django.contrib.auth.forms import PasswordResetForm
import datetime
from django.conf import settings


def get_languages():
    return Language.objects.all().order_by('id')

def get_organisations():
    return Tenant.objects.all().order_by('id')

def get_frameworks():
    lang = settings.LANGUAGE_CODE.upper()
    print("==============>Lang:",lang)
    return Category.objects.filter(type='framework', language=lang).order_by('id')

def get_categories():
    lang = settings.LANGUAGE_CODE.upper()
    print("==============>Lang:",lang)
    return Category.objects.filter(type='category', language=lang).order_by('id')

def get_subcategories():
    lang = settings.LANGUAGE_CODE.upper()
    print("==============>Lang:", lang)
    return Category.objects.filter(type='sub_category', language=lang).order_by('id')

class DivErrorList(ErrorList):
    def __str__(self):

        return self.as_divs()
    def as_divs(self):
        if not self: return ''

        return '<div class="errorlist">%s</div>' % ''.join(['<div class="text-danger">%s</div>' % e for e in self])

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email', 'name': 'email','placeholder':'Email'}),
        error_messages=dict(
            invalid="Enter a valid email address"),max_length=100,
        required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password', 'name': 'password','placeholder':'Password'}),max_length=100, required=True)

    class Meta:
        fields = ['email','password']

    def clean_email(self):
        try:
            email = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("The username does not exist."))
        return self.cleaned_data['email']


class PasswordReset(PasswordResetForm):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email', 'name': 'email', 'placeholder': 'Email'}),
        error_messages=dict(
            invalid="Enter a valid email address."),max_length=100,
        required=True)

    class Meta:
        fields = ['email']

    def clean_email(self):
        try:
            email = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("The email does not exist."))
        return self.cleaned_data['email']





USER_TYPE_CHOICE = [
    ('user', 'User'),
    ('admin', 'Admin'),
]


class CreateUserForm(forms.ModelForm):
    f_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'f_name', 'placeholder': 'First name'}),
        max_length=50, required=True)
    l_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'l_name', 'placeholder': 'Last name'}),
        max_length=50, required=True)
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email', 'name': 'email', 'placeholder': 'Email'}),
        error_messages=dict(
            invalid="Enter a valid email address"), max_length=100, required=True)
    tenant = forms.ModelChoiceField(queryset=get_organisations(), widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'tenant'}), required=False)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICE, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'user_type'}), required=True)
    language = forms.ModelChoiceField(queryset=get_languages(), widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'language'}), required=True)
    industry = forms.CharField(widget=forms.Select(choices=[("1", "1"), ("2", "2")], attrs={
        'class': 'form-control', 'name': 'industry'}))


    class Meta:
        model = User
        fields = ['email','f_name','l_name','tenant','user_type','language','industry']

    def clean_email(self):
        try:
            email = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("The email is already in use."))



class UserProfileUpdateForm(forms.ModelForm):
    f_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'f_name'}),
        max_length=50, required=True)
    l_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'l_name'}),
        max_length=50, required=True)
    country = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'country'}),
        max_length=50, required=True)
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'city'}),
        max_length=50, required=True)
    address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'address'}),
        max_length=50, required=True)
    postal_code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'postal_address'}),
        max_length=50, required=True)
    image = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'form-control', 'multiple': False, 'name': 'image'}),required=False)

    bio = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'bio','rows': 3, 'cols':9}),
        max_length=50, required=False)

    class Meta:
        model = User
        fields = ['f_name','l_name','country','city','address','postal_code','image','bio']






class UploadFileForm(forms.Form):
    file_upload = forms.FileField(label='Select a file',help_text='max. 42 megabytes')

    class Meta:
        fields = ['file_upload']

class UserUpadateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email','f_name','l_name','tenant','user_type','language']



year_dropdown = []
for y in range(2011, (datetime.datetime.now().year + 5)):
    year_dropdown.append((y,y))
status_dropdown = [
    ('All','All'),
    ('Attempted','Attempted'),
    ('Not Attempted','Not Attempted'),
    ('Not Applicable','Not Applicable')
]
class AddDataForm(forms.Form):
    lang = settings.LANGUAGE_CODE.upper()
    query_framework = Category.objects.filter(type='framework', language=lang)
    # print("Query_framework:----------", query_framework)
    # print("Language in forms.py:-------------",lang)
    query_category = Category.objects.filter(type='category', language=lang)
    # print("Query_category:----------- ", query_category)
    query_sub_category = Category.objects.filter(type='sub_category', language=lang)
    # print("Query_sub_category:-------- ", query_sub_category)
    framework = forms.ModelChoiceField(queryset=query_framework,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left'}), required=False)
    category = forms.ModelChoiceField(queryset=query_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left'}),required=False)
    sub_category = forms.ModelChoiceField(queryset=query_sub_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left','maxlength':'12'}), required=False)
    year = forms.ChoiceField(choices = year_dropdown, initial=datetime.datetime.now().year,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'style':'float:left'}), required = False)

    # def __init__(self, *args, **kwargs):
    #     super(AddDataForm, self).__init__(*args, **kwargs)
    #     self.fields['framework'].queryset = get_frameworks()
 

class StatusForm(forms.Form):
    query_framework = Category.objects.filter(type='framework')
    query_category = Category.objects.filter(type='category')
    query_sub_category = Category.objects.filter(type='sub_category')
    framework = forms.ModelChoiceField(queryset=query_framework,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left'}), required=False)
    category = forms.ModelChoiceField(queryset=query_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left'}),required=False)
    sub_category = forms.ModelChoiceField(queryset=query_sub_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left','maxlength':'12'}), required=False)

class StatusForm1(forms.Form):
    query_framework = Category.objects.filter(type='framework')
    query_category = Category.objects.filter(type='category')
    query_sub_category = Category.objects.filter(type='sub_category')
    framework = forms.ModelChoiceField(queryset=query_framework, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}), required=False)
    category = forms.ModelChoiceField(queryset=query_category, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}), required=False)
    sub_category = forms.ModelChoiceField(queryset=query_sub_category, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'maxlength': '12'}), required=False)
    year = forms.ChoiceField(choices=year_dropdown, initial=datetime.datetime.now().year, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}), required=False)



class DataStatusForm(forms.Form):
    query_framework = Category.objects.filter(type='framework')
    query_category = Category.objects.filter(type='category')
    query_sub_category = Category.objects.filter(type='sub_category')
    framework = forms.ModelChoiceField(queryset=query_framework,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}), required=False)
    category = forms.ModelChoiceField(queryset=query_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}),required=False)
    sub_category = forms.ModelChoiceField(queryset=query_sub_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','maxlength':'12'}), required=False)
    year = forms.ChoiceField(choices = year_dropdown, initial=datetime.datetime.now().year,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}), required = False)
    status = forms.ChoiceField(choices = status_dropdown, initial=status_dropdown[0][0] ,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text'}), required = False)



class TodoForm(forms.Form):
    query_framework = Category.objects.filter(type='framework')
    query_category = Category.objects.filter(type='category')
    query_sub_category = Category.objects.filter(type='sub_category')
    framework = forms.ModelChoiceField(queryset=query_framework,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left'}), required=False)
    category = forms.ModelChoiceField(queryset=query_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left'}),required=False)
    sub_category = forms.ModelChoiceField(queryset=query_sub_category,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text','style':'float:left','maxlength':'12'}), required=False)

class FrameworCategoryProgressForm(forms.Form):
    query_framework = Category.objects.filter(type='framework')
    framework = forms.ModelChoiceField(queryset=query_framework,widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'style': 'padding-right:2rem;padding-left:2rem'}), required=False)
    
    # display:flex;justify-content:center;align-items:center
