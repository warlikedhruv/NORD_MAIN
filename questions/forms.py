from itertools import filterfalse
from django import forms
from users.models import *
from django.utils.translation import ugettext_lazy as _
from organisations.models import *
from django.forms.utils import ErrorList
from questions.models import *
from languages.models import *
from django.contrib.auth.forms import PasswordResetForm
import datetime

def get_languages():
    return Language.objects.all().order_by('id')

def get_organisations():
    return Tenant.objects.all().order_by('id')

def get_frameworks():
    return  Category.objects.filter(type='framework').order_by('id')

def get_categories():
    return Category.objects.filter(type='category').order_by('id')

def get_subcategories():
    return Category.objects.filter(type='sub_category').order_by('id')


class CreateQuestionForm(forms.Form):

    framework = forms.ModelChoiceField(queryset=get_frameworks(),widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'framework'}), required=True)

    category = forms.ModelChoiceField(queryset=get_categories(),widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'category'}),required=True)
    sub_category = forms.ModelChoiceField(queryset=get_subcategories(),widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'sub_category'}), required=True)
    question = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'question', 'placeholder': 'Question','rows': 7, 'cols':30}),
        max_length=500, required=True)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'description', 'placeholder': 'Description','rows': 7, 'cols':30}),
        max_length=500, required=True)
    unit = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'unit', 'placeholder': 'Unit'}),
        max_length=100, required=True)
    language = forms.ModelChoiceField(queryset=get_languages(), widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'language'}), required=True)
    industry = forms.CharField(widget=forms.Select(choices=[("1", "1"), ("2", "2")], attrs={
        'class': 'form-control', 'name': 'industry'}))

    class Meta:
        fields = ['framework','category','sub_category','question','description','unit','language','industry']

    def clean_question(self):
        try:
            question = Question.objects.get(question__iexact=self.cleaned_data['question'])
        except Question.DoesNotExist:
            return self.cleaned_data['question']
        raise forms.ValidationError(_("The question already exists."))


class QuestionUpdateForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['question','description','unit']




class CreateCatesForm(forms.ModelForm):
    TYPE_CHOICE = [

        ('framework', 'framework'),
        ('category', 'category'),
        ('sub_category', 'sub_category')

    ]

    name = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'name': 'name',
                                                        'placeholder': 'Name'}), max_length=500, required=True)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'description', 'placeholder': 'Description', 'rows': 4,
               'cols': 10}),max_length=500, required=True)
    type = forms.ChoiceField(choices=TYPE_CHOICE, widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'type'}), required=True)
    language = forms.ModelChoiceField(queryset=get_languages(), widget=forms.Select(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'language'}), required=True)

    class Meta:
        model = Category
        fields = ['name','description','type','language']




class CatesMappingUpdateForm(forms.ModelForm):

    class Meta:
        model = CategoryMapping
        fields = ['framework','category','sub_category']



class QuestionAnswerForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'question', 'placeholder': 'Question','rows': 7, 'cols':30,'readonly':'readonly'}),
        max_length=500, required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'description', 'placeholder': 'Description','rows': 7, 'cols':30,'readonly':'readonly'}),
        max_length=500, required=False)
    unit = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'unit', 'placeholder': 'Unit','readonly':'readonly'}),
        max_length=100, required=False)
    code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'code', 'placeholder': 'Code','readonly':'readonly'}),
        max_length=100, required=False)
    value = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'name': 'value',
                                                        'placeholder': 'Max Char 500', 'rows': 4,
                                                        'cols': 10}), max_length=500, required=False)

    comment = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'type': 'text', 'name': 'comment', 'placeholder': 'Max Char 500', 'rows': 4,
               'cols': 10}), max_length=500, required=False)
    file = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'form-control', 'multiple': True, 'name': 'file'}), required=False)
    optional = forms.BooleanField(initial=False, required=False)
    goals = forms.BooleanField(initial=False, required=False)


    

