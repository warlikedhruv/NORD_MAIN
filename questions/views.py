from django.shortcuts import render
from django.contrib.auth.decorators import (login_required,user_passes_test)
from users.permissions import *
from .forms import *
from questions.models import *
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from users.forms import DivErrorList
from django.contrib import messages
import random
from django.core.files.storage import FileSystemStorage
import csv,os
from datetime import datetime
from django.shortcuts import get_object_or_404
import re
import pandas as pd
from pandas import Series
from django.utils.translation import gettext as _
from django.db.models.query_utils import Q
from django.utils import translation
# Create your views here.


@user_passes_test(check_viewing_rights_admin)
def create_question(request):
    if request.method == 'POST':
        try:
            q_form = CreateQuestionForm(request.POST)
            if q_form.is_valid():
                print('Form Valid..')
                framework = str(q_form.cleaned_data['framework'])
                category = str(q_form.cleaned_data['category'])
                sub_category = str(q_form.cleaned_data['sub_category'])
                question = str(q_form.cleaned_data['question'])
                description = str(q_form.cleaned_data['description'])
                unit = str(q_form.cleaned_data['unit'])
                language = str(q_form.cleaned_data['language'])
                industry = str(q_form.cleaned_data['industry'])
                print(industry)


                if (Category.objects.filter(type='framework').filter(name__iexact=framework)).exists():
                    framework_obj = Category.objects.filter(type='framework').filter(
                        name__iexact=framework)
                    framework_obj = framework_obj[0]
                else:
                    framework_obj = Category.objects.create(name=framework, type='framework')

                if Category.objects.filter(type='category').filter(name__iexact=category).exists():
                    category_obj = Category.objects.filter(type='category').filter(
                        name__iexact=category)
                    category_obj = category_obj[0]
                else:
                    category_obj = Category.objects.create(type='category', name=category)
                if Category.objects.filter(type='sub_category').filter(
                        name__iexact=sub_category).exists():
                    sub_category_obj = Category.objects.filter(type='sub_category').filter(
                        name__iexact=sub_category)
                    sub_category_obj = sub_category_obj[0]
                else:
                    sub_category_obj = Category.objects.create(type='sub_category', name=sub_category)
                print('Reached 55')
                if (CategoryMapping.objects.filter(framework=framework_obj).filter(category=category_obj).filter(
                        sub_category=sub_category_obj)).exists():
                    cates_mapping_obj = CategoryMapping.objects.filter(framework=framework_obj).filter(
                        category=category_obj).filter(sub_category=sub_category_obj)
                    cates_mapping_obj = cates_mapping_obj[0]
                else:
                    cates_mapping_obj = CategoryMapping.objects.create(framework=framework_obj,
                                                                     category=category_obj,
                                                                     sub_category=sub_category_obj)
                print('Reached 65')
                if Question.objects.filter(question__iexact=question).exists():
                    ques_obj = Question.objects.filter(question__iexact=question)
                    ques_obj = ques_obj[0]
                else:
                    ques_obj = Question.objects.create(question=question,
                                                             description=description,
                                                             unit=unit,
                                                             language=language,
                                                             industry=industry)
                print('Reached 72')
                if QuestionCategoryMapping.objects.filter(ques_map=ques_obj).filter(cate=cates_mapping_obj).exists():
                    print("This mapping and question already exist")
                else:
                    mapping_obj = QuestionCategoryMapping.objects.create(ques_map=ques_obj, cate=cates_mapping_obj)
                ## Stroing Temp Answer model when each question is created..
                Answer.objects.create(
                    question = ques_obj,
                    organisation = None,
                    user = request.user)
                messages.success(request, f'New question record created successfully!')
                return redirect('create-question')
            else:
                print(q_form.errors)
        except Exception as e:
            print(e)
            messages.error(request, f'Something happened in there. Please try again.')
            return redirect('create-question')
    else:
        q_form = CreateQuestionForm()
    return render(request, 'question/create_question.html', {'q_form':q_form})



@user_passes_test(check_viewing_rights_admin)
def update_question(request,pk):
    ques_cat_tab = get_object_or_404(QuestionCategoryMapping, pk=pk)
    q_tab = get_object_or_404(Question, pk=ques_cat_tab.ques_map.id)
    c_tab = get_object_or_404(CategoryMapping, pk=ques_cat_tab.cate.id)
    if request.method == 'POST':
        try:
            q_form = QuestionUpdateForm(request.POST, instance=q_tab, error_class=DivErrorList)
            c_form = CatesMappingUpdateForm(request.POST,instance=c_tab, error_class=DivErrorList)


            if q_form.is_valid() and c_form.is_valid():
                q_form.save()
                c_form.save()
                messages.success(request, _("Record has been updated successfully!"))
                return redirect(reverse('question'))
        except Exception as e:
            print(e)
            messages.error(request, _("No record found!"))
            return redirect(reverse('question'))

    else:
        q_form = QuestionUpdateForm(instance=q_tab)
        c_form = CatesMappingUpdateForm(instance=c_tab)
    context = {'q_form': q_form, 'c_form': c_form, "q_id": pk}
    return render(request, 'question/edit_question.html', context)

@user_passes_test(check_viewing_rights_admin)
def delete_question(request,pk):
    try:
        q_cat_mapping = QuestionCategoryMapping.objects.get(id=pk)
        qtn = Question.objects.get(id=q_cat_mapping.ques_map.id)
        print(pk)
        qtn.delete()
        q_cat_mapping.delete()
        messages.success(request, _("Record deleted successfully."))
        return redirect('/question')
    except Exception as e:
        messages.error(request, _("Some error occurred!. Please try again."))
        return redirect(reverse('question'))


@user_passes_test(check_viewing_rights_admin)
def upload_questions(request):
    excel_pattern = re.compile(r'^.*\.xl(sx|s|tx|t|sm)$', re.IGNORECASE)

    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        if str(file).endswith('.csv'):
            file_s = FileSystemStorage()
            file_name = random.randint(1, 10000)
            file_s.save(f'{file_name}.csv', file)
            try:
                data = pd.read_csv(open(f'media/{file_name}.csv',encoding="utf8"))
                for i in range(data['framework'].size):
                    print(i)
                    if (Category.objects.filter(type='framework').filter(name__iexact=data.loc[i, 'framework'])).exists():
                        framework_obj = Category.objects.filter(type='framework').filter(
                            name__iexact=data.loc[i, 'framework'])
                        framework_obj = framework_obj[0]
                    else:
                        framework_obj = Category.objects.create(name=data.loc[i, 'framework'], type='framework')
                   
                    if Category.objects.filter(type='category').filter(name__iexact=data.loc[i, 'category']).exists():

                        category_obj = Category.objects.filter(type='category').filter(
                            name__iexact=data.loc[i, 'category'])
                        category_obj = category_obj[0]
                    else:
                        category_obj = Category.objects.create(type='category', name=data.loc[i, 'category'])
                  
                    if Category.objects.filter(type='sub_category').filter(
                            name__iexact=data.loc[i, 'sub_category']).exists():
                        sub_category_obj = Category.objects.filter(type='sub_category').filter(
                            name__iexact=data.loc[i, 'sub_category'])
                        sub_category_obj = sub_category_obj[0]
                    else:
                        sub_category_obj = Category.objects.create(type='sub_category',
                                                                name=data.loc[i, 'sub_category'])
                   
                    if (CategoryMapping.objects.filter(framework=framework_obj).filter(category=category_obj).filter(
                            sub_category=sub_category_obj)).exists():
                        cates_mapping_obj = CategoryMapping.objects.filter(framework=framework_obj).filter(
                            category=category_obj).filter(sub_category=sub_category_obj)
                        cates_mapping_obj = cates_mapping_obj[0]
                    else:
                        cates_mapping_obj = CategoryMapping.objects.create(framework=framework_obj,
                                                                         category=category_obj,
                                                                         sub_category=sub_category_obj)
                 
                    if Question.objects.filter(question__iexact=data.loc[i, 'question']).exists():
                        ques_obj = Question.objects.filter(question__iexact=data.loc[i, 'question'])
                        ques_obj = ques_obj[0]
                    else:
                        ques_obj = Question.objects.create(question=data.loc[i, 'question'],
                                                                 description=data.loc[i, 'description'],
                                                                 unit=data.loc[i, 'units'],
                                                                 code =data.loc[i, 'disclosure_number'],
                                                                 industry=data.loc[i, 'industry'],
                                                                 language=data.loc[i, 'language_code']
                                                                 )
                    ## Stroing Temp Answer model when each question is created..
                    Answer.objects.create(question = ques_obj,organisation = None,user = request.user)

                    if QuestionCategoryMapping.objects.filter(ques_map=ques_obj).filter(cate=cates_mapping_obj).exists():
                        print("This mapping and question already exist")

                    else:
                        mapping_obj = QuestionCategoryMapping.objects.create(ques_map=ques_obj, cate=cates_mapping_obj)
                   

                    
                messages.success(request, 'Questions successfully added.')
                return redirect('question')
            except Exception as e:
                print('############# Except Block #############')
                messages.error(request, 'Please check the file has the correct fields.')
                print(e)
            finally:
                del data
                try:
                    os.remove(f'media/{file_name}.csv')
                except Exception as e:
                    print(e)
        elif excel_pattern.match(str(file)):
            file_s = FileSystemStorage()
            file_name = random.randint(1, 10000)
            file_s.save(f'{file_name}.xlsx', file)
            try:
                data = pd.read_excel(f'media/{file_name}.xlsx',engine='openpyxl')
                
                for i in range(data['framework'].size):
                    print(i)
                    if (Category.objects.filter(type='framework')\
                        .filter(Q(name__iexact=data.loc[i, 'framework']) & (Q(language__iexact=data.loc[i, 'language_code'])))).exists():
                        framework_obj = Category.objects.filter(type='framework')\
                        .filter(Q(name__iexact=data.loc[i, 'framework']) & (Q(language__iexact=data.loc[i, 'language_code'])))
                        framework_obj = framework_obj[0]
                    else:
                        framework_obj = Category.objects.create(name=data.loc[i, 'framework'],
                         type='framework',
                         language=data.loc[i, 'language_code'])
                   
                    if Category.objects.filter(type='category')\
                        .filter(Q(name__iexact=data.loc[i, 'category']) & Q(language__iexact=data.loc[i, 'language_code'])).exists():
                        category_obj = Category.objects.filter(type='category')\
                            .filter(Q(name__iexact=data.loc[i, 'category']) & Q(language__iexact=data.loc[i, 'language_code']))
                        category_obj = category_obj[0]
                    else:
                        category_obj = Category.objects.create(type='category', name=data.loc[i, 'category'],language=data.loc[i, 'language_code'])
                   
                    if Category.objects.filter(type='sub_category')\
                        .filter(Q(name__iexact=data.loc[i, 'sub_category']) & Q(language__iexact=data.loc[i, 'language_code'])).exists():
                        sub_category_obj = Category.objects.filter(type='sub_category')\
                            .filter(Q(name__iexact=data.loc[i, 'sub_category']) & Q(language__iexact=data.loc[i, 'language_code']))
                        sub_category_obj = sub_category_obj[0]
                    else:
                        sub_category_obj = Category.objects.create(type='sub_category',
                                                                name=data.loc[i, 'sub_category'],
                                                                language=data.loc[i, 'language_code'])
                    
                    if (CategoryMapping.objects.filter(framework=framework_obj).filter(category=category_obj).filter(
                            sub_category=sub_category_obj)).exists():
                        cates_mapping_obj = CategoryMapping.objects.filter(framework=framework_obj).filter(
                            category=category_obj).filter(sub_category=sub_category_obj)
                        cates_mapping_obj = cates_mapping_obj[0]
                    else:
                        cates_mapping_obj = CategoryMapping.objects.create(framework=framework_obj,
                                                                         category=category_obj,
                                                                         sub_category=sub_category_obj)
                   
                    if Question.objects.filter(question__iexact=data.loc[i, 'question']).exists():
                        ques_obj = Question.objects.filter(question__iexact=data.loc[i, 'question'])
                        ques_obj = ques_obj[0]
                    else:
                        ques_obj = Question.objects.create(question=data.loc[i, 'question'],
                                                                 description=data.loc[i, 'description'],
                                                                 unit=data.loc[i, 'units'],
                                                                 code =data.loc[i, 'disclosure_number'],
                                                                 industry=data.loc[i, 'industry'],
                                                                 language=data.loc[i, 'language_code']
                                                                 )
                        ## Stroing Temp Answer model when each question is created..
                        Answer.objects.create(question = ques_obj,organisation = None,user = request.user)

                    if QuestionCategoryMapping.objects.filter(ques_map=ques_obj).filter(cate=cates_mapping_obj).exists():
                        print("This mapping and question already exist")
                    else:
                        mapping_obj = QuestionCategoryMapping.objects.create(ques_map=ques_obj, cate=cates_mapping_obj)
                  

               
                messages.success(request, 'Questions successfully added.')
                return redirect('question')
            except Exception as e:
                messages.error(request, e)
                print(e)
            finally:
                try:
                    os.remove(f'media/{file_name}.xlsx')
                except Exception as e:
                    print(e)
        else:
            messages.error(request, 'Unsupported file extension!.')
            return redirect('upload-question')
    return render(request, 'question/upload_questions.html')


@user_passes_test(check_viewing_rights_admin)
def create_cates(request):
    if request.method == 'POST':
        try:
            cates_form = CreateCatesForm(request.POST)
            if cates_form.is_valid():
                cates_form.save()
                messages.success(request, f'New cates record created successfully!')
                return redirect('create-cates')
        except Exception as e:
            messages.error(request, f'Something happened in there. Please try again.')
            return redirect('create-cates')
    else:
        cates_form = CreateCatesForm()
    return render(request, 'question/create_cates.html', {'cates_form': cates_form})
