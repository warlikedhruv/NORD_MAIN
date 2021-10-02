from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.forms import formset_factory
from users.models import User
from django.contrib import auth
from organisations.models import *
from questions.models import *
import json as simplejson
from django.http import HttpResponse
from django.db import connection
from django.utils.translation import gettext as _
from django.core.paginator import (Paginator,
                                   EmptyPage,
                                   PageNotAnInteger)
from documents.models import *
from .filters import *
from .permissions import check_viewing_rights_admin
from .forms import *
from questions.forms import *
from django.contrib.auth.decorators import (login_required,user_passes_test)
from django.contrib.auth.decorators import (login_required,user_passes_test)
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail,  BadHeaderError
from django.conf import settings
from django.utils import translation
from django.contrib.auth import login, authenticate
import random
from django.core.files.storage import FileSystemStorage
import csv,os
from datetime import datetime
from django.shortcuts import get_object_or_404
import re
import pandas as pd
from pandas import Series
from django.http import JsonResponse
from itertools import chain
from fpdf import FPDF
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
# Create your views here.
def password_reset(request):
    if request.method == "POST":
        form = PasswordReset(request.POST)
        if form.is_valid():
            email_ = form.cleaned_data['email']
            current_site = get_current_site(request)
            mail_subject = "Reset your NordESG.com password"
            user_found = User.objects.filter(Q(email=email_))
            if user_found.exists():
                for user in user_found:
                    c = {
                        'user': user,
                        'site_name': 'NordESG',
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': settings.PROTOCOL,
                    }
                    info = render_to_string('users/password_reset_email.html', c)
                    try:
                        send_mail(mail_subject, info , settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except Exception as e:
                        messages.warning(request, 'An unexpected error occurred. Please check your network connection or try again later.')
                        return redirect('password-reset')
                    return redirect('password-reset-done')
    else:
        form = PasswordReset()
    return render(request,'users/password_reset.html', {'form': form})

def set_language(request):
    pass
#     language = request.POST.get('language', settings.LANGUAGE_CODE)
#     translation.activate(language)
#     request.session[translation.LANGUAGE_SESSION_KEY] = language

#     return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def error_404(request,*args):
    return render(request, 'users/page-404.html')

def error_500(request,*args):
    return render(request, 'users/page-500.html')

def error_403(request,*args):
    return render(request, 'users/page-403.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user_email = User.objects.get(email=email)
                user = authenticate(request, email=user_email, password=password)
                if user is not None:
                    if user.is_superuser or user.user_type=="admin":
                        login(request, user)
                        return redirect('admin-dashboard')
                    elif user.is_active:
                        login(request, user)
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'An unknown error occurred. Please try again.')
                        return redirect('user-login')
                else:
                    messages.error(request, 'Incorrect username or password.')
                    return redirect('user-login')

            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials')
                return redirect('login')
            except Exception as e:
                messages.error(request,
                               "Something went wrong and we couldn't fetch some critical info. Please check your network connection or try again later.")
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required(login_url="/user-login")
def user_logout(request):
    try:
        auth.logout(request)
        return redirect('user-login')
    except Exception as e:
        pass



@user_passes_test(check_viewing_rights_admin)
def admin_dashboard(request):
    organizations= Tenant.objects.all().count()
    total_users = User.objects.all().count()
    questions = Question.objects.all().count()
    frameworks = Category.objects.filter(type__contains="framework").count()
    context = {'total_users': total_users,'organizations':organizations,'questions':questions,'frameworks':frameworks}
    return render(request,'users/admin_dashboard.html',context)

@user_passes_test(check_viewing_rights_admin)
def organizations(request):

    orgs_tab = Tenant.objects.all().order_by('-id')
    org_filter = OrganisationFilter(request.GET, queryset=orgs_tab)
    orgs_tab = org_filter.qs

    page = request.GET.get('page', 1)

    paginator = Paginator(orgs_tab, 10)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1)
    except EmptyPage:
        lists = paginator.page(paginator.num_pages)

    return render(request, 'organisation/organization.html',{'lists': lists,'org_filter':org_filter})


@user_passes_test(check_viewing_rights_admin)
def users_detail(request):
    users_tab = User.objects.all().order_by('-id')
    user_filter = UserFilter(request.GET, queryset=users_tab)
    users_tab = user_filter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(users_tab, 10)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1)
    except EmptyPage:
        lists = paginator.page(paginator.num_pages)

    return render(request, 'users/users_detail.html',{'lists': lists,'user_filter':user_filter})


@user_passes_test(check_viewing_rights_admin)
def stakeholders(request):
    return render(request, 'stakeholder/stakeholder.html', {})



@user_passes_test(check_viewing_rights_admin)
def questions(request):
    q_tab = QuestionCategoryMapping.objects.all().order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(q_tab, 10)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1)
    except EmptyPage:
        lists = paginator.page(paginator.num_pages)
    return render(request, 'question/question.html',{'lists': lists})


@login_required(login_url="/user-login")
def user_profile(request):
    return render(request,'users/profile.html')





@login_required(login_url="/user-login")
def user_profile_update(request):
    if request.method == 'POST':
        p_form = UserProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user)
        if p_form.is_valid():
            p_form.save()
            
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        p_form = UserProfileUpdateForm(instance=request.user)
    return render(request,'users/profile_update.html',{'p_form': p_form})



@user_passes_test(check_viewing_rights_admin)
def create_user(request):
    if request.method == 'POST':
        try:
            user_form = CreateUserForm(request.POST)
            if user_form.is_valid():
                print('User Entered')
                user_email = str(user_form.cleaned_data['email'])
                lang = str(user_form.cleaned_data['language'])
                user_type = str(user_form.cleaned_data['user_type'])
                industry = str(user_form.cleaned_data['industry'])

                user = user_form.save(commit=False)
                if user_type=="admin":
                    user.is_staff=True
                user.save()
                print('User saved')
                user_ = User.objects.get(email__iexact=user_email)
                print('Setting up password reset mail..')
                subject = "Set password"
                current_site = get_current_site(request)
                c = {
                    "email": user_.email,
                    'domain': current_site.domain,
                    'site_name': 'NordESG',
                    "uid": urlsafe_base64_encode(force_bytes(user_.pk)),
                    "user": user_,
                    'token': default_token_generator.make_token(user_),
                    'protocol': settings.PROTOCOL,
                }
                print('Getting User Language')
                if lang.endswith('de'):
                    info = render_to_string("users/password_set_email_de.txt", c)
                else:
                    info = render_to_string("users/password_set_email_en.txt", c)
                print('Sending Mail..')
                try:
                    send_mail(subject, info, settings.DEFAULT_FROM_EMAIL, [user_.email], fail_silently=False)
                    print('Mail sent..')
                except BadHeaderError:
                    messages.error(request, 'Invalid header found.')
                    return redirect('create-user')
            messages.success(request, f'New User record created successfully!')
            return redirect('create-user')
        except Exception as e:
            print(e)
            messages.error(request, f'Something happened in there. Please try again.')
            return redirect('create-user')
    else:
        user_form = CreateUserForm()
    return render(request, 'users/create_user.html', {'user_form': user_form})



def password_reset(request):
    if request.method == "POST":
        form = PasswordReset(request.POST)
        if form.is_valid():
            email_ = form.cleaned_data['email']
            current_site = get_current_site(request)
            mail_subject = "Reset your NordESG.com password"
            user_found = User.objects.filter(Q(email=email_))
            if user_found.exists():
                for user in user_found:
                    c = {
                        'user': user,
                        'site_name': 'NordESG',
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': settings.PROTOCOL,
                    }
                    info = render_to_string('users/password_reset_email.html', c)
                    try:
                        send_mail(mail_subject, info , settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except Exception as e:
                        messages.warning(request, 'An unexpected error occurred. Please check your network connection or try again later.')
                        return redirect('password-reset')
                    return redirect('password-reset-done')
    else:
        form = PasswordReset()
    return render(request,'users/password_reset.html', {'form': form})


@user_passes_test(check_viewing_rights_admin)
def update_user(request,pk):
    try:
        u_tab = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            user_form = UserUpadateForm(request.POST, instance=u_tab, error_class=DivErrorList)

            if user_form.is_valid():
                user_form.save()
                messages.success(request, _("Record has been updated successfully!"))
                return redirect(reverse('user-detail'))
        else:
            user_form = UserUpadateForm(instance=u_tab)

        context = {'user_form': user_form, "u_id": pk}
        return render(request, 'users/edit_user.html', context)
    except Exception as e:
        messages.error(request, _("No record found!"))
        return redirect(reverse('user-detail'))



@user_passes_test(check_viewing_rights_admin)
def delete_user(request,pk):
    try:
        u = User.objects.get(id=pk)
        u.delete()
        messages.success(request, _("Record deleted successfully."))
        return redirect('user-detail')
    except Exception as e:
        messages.error(request, _("Some error occurred!. Please try again."))
        return redirect(reverse('user-detail'))



@user_passes_test(check_viewing_rights_admin)
def users_detail(request):
    users_tab = User.objects.all().order_by('-id')
    user_filter = UserFilter(request.GET, queryset=users_tab)
    users_tab = user_filter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(users_tab, 10)
    try:
        lists = paginator.page(page)
    except PageNotAnInteger:
        lists = paginator.page(1)
    except EmptyPage:
        lists = paginator.page(paginator.num_pages)

    return render(request, 'users/users_detail.html',{'lists': lists,'user_filter':user_filter})

######################################## User DashBoard Code ####################################
def get_user_language():
    user_language = settings.LANGUAGE_CODE
    return user_language.upper()


def randomHex():
    import random
    random_number = random.randint(0,16777215)
    hex_number = str(hex(random_number))
    hex_number ='#'+ hex_number[2:]
    return hex_number

@login_required(login_url="/user-login")
def user_dashboard(request):
    from django.conf import settings
    print("-------------------->",settings.LANGUAGE_CODE)
    print('Choosen Language...................',get_user_language())
    from django.utils import translation
    if request.method == "POST":
        categoryform = FrameworCategoryProgressForm(request.POST)
        if categoryform.is_valid():
            if categoryform.cleaned_data['framework'] is None:
                categoryformoptions = request.session.get('category_progress_form')
            else:
                # Stroing Session if filter form is valid
                categoryformoptions = categoryform.cleaned_data
                categoryformoptions['framework']=categoryformoptions['framework'].id
                #print(categoryform)
                request.session['category_progress_form'] = categoryformoptions
                print('Current category_progress_form  session: ',request.session.get('category_progress_form'))
                ###############################################################################
            category,category_total,category_answers=progressPerCategory(categoryformoptions['framework'],request.user.tenant.id,datetime.now().year,get_user_language())
            category_resultsText=[]
            category_results =[]
            category_resultsNum = []
            for i in range(len(category)):
                res=round(category_answers[i]/category_total[i],2)
                category_results.append(res)
                category_resultsText.append('{}/{} = {}'.format(category_answers[i],category_total[i],res))
            
            for i in category_resultsText:  # splitting text progress values
                temp = i.split(" ")
                temp = temp[0].split("/")
                category_resultsNum.append(
                {"current": int(temp[0]) * 100 / int(temp[1])})
            

            framework,questionCount,answerCount = progressPerFramework(request.user.tenant.id,datetime.now().year,get_user_language())
            frameworkProgressResults = []
            frameworkProgressResultsText = []
            frameworkProgressResultsNum = []
            for i in range(len(framework)):
                res = round(answerCount[i]/questionCount[i],2)
                frameworkProgressResults.append(res)
                frameworkProgressResultsText.append('{}/{} = {}'.format(answerCount[i],questionCount[i],res))

            for i in frameworkProgressResultsText:  # splitting text progress values
                temp = i.split(" ")
                temp = temp[0].split("/")
                frameworkProgressResultsNum.append(
                {"current": (int(temp[0]) * 100 / int(temp[1]))*100})

            org_users = Tenant.objects.all().get(id=request.user.tenant.id).tenant_1.all().exclude(email=request.user.email)
            chart_color=[ randomHex() for i in range(len(framework))]
            chart_color2=[ randomHex() for i in range(len(framework))]
            print(zip(framework,frameworkProgressResultsText,  frameworkProgressResultsNum))
            data = {
                    'frameworks':zip(framework,frameworkProgressResultsText,  frameworkProgressResultsNum),
                    'org_users':org_users,
                    'framework':framework,
                    'frameworkProgressResults':frameworkProgressResults,
                    'chart_color':chart_color,
                    'chart_color2':chart_color2,
                    'categoryform':FrameworCategoryProgressForm(initial=request.session.get('category_progress_form')),
                    'categoryresults':zip(category,category_resultsText, category_resultsNum),
                    'categorys':category,
                    'categoryProgressResults':category_results
                    }

    else:
        if request.session.get('category_progress_form')==None:
            framework_id = Category.objects.filter(type='framework')[0].id
            pass
        else:
            framework_id = request.session.get('category_progress_form')['framework']

        category,category_total,category_answers=progressPerCategory(framework_id,request.user.tenant.id,datetime.now().year,get_user_language())
        category_resultsText=[]
        category_results =[]
        category_resultsNum = []

        for i in range(len(category)):
            res=round(category_answers[i]/category_total[i],2)
            category_results.append(res)
            category_resultsText.append('{}/{} = {}'.format(category_answers[i],category_total[i],res))
        
        for i in category_resultsText: #splitting text progress values
            temp = i.split(" ")
            temp = temp[0].split("/")
            category_resultsNum.append({"current": (int(temp[0]) * 100 / int(temp[1]))*100})
        print(category_resultsNum)

        framework,questionCount,answerCount = progressPerFramework(request.user.tenant.id,datetime.now().year,get_user_language())
        frameworkProgressResults = []
        frameworkProgressResultsText = []
        frameworkProgressResultsNum=[]

        for i in range(len(framework)):
            res = round(answerCount[i]/questionCount[i],2)
            frameworkProgressResults.append(res)
            frameworkProgressResultsText.append('{}/{} = {}'.format(answerCount[i],questionCount[i],res))

        for i in frameworkProgressResultsText: #splitting text progress values
            temp = i.split(" ")
            temp = temp[0].split("/")
            frameworkProgressResultsNum.append({"current": int(temp[0]) * 100 / int(temp[1])})
        print(frameworkProgressResultsNum)

        org_users = Tenant.objects.all().get(id=request.user.tenant.id).tenant_1.all().exclude(email=request.user.email)
        chart_color=[ randomHex() for i in range(len(framework))]
        chart_color2=[ randomHex() for i in range(len(framework))]

        # Setting language cookie
        # from django.utils import translation
        # user_language = 'de' 
        # translation.activate(user_language)
        #response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        print('category progress form..',request.session.get('category_progress_form'))
        print(framework,frameworkProgressResultsText,  frameworkProgressResultsNum)
        data = {
                'frameworks':zip(framework,frameworkProgressResultsText, frameworkProgressResultsNum),
                'org_users':org_users,
                'framework':framework,
                'frameworkProgressResults':frameworkProgressResults,
                'chart_color':chart_color,
                'chart_color2':chart_color2,
                'categoryform':FrameworCategoryProgressForm(initial=request.session.get('category_progress_form')),
                'categoryresults':zip(category,category_resultsText, category_resultsNum ),
                'categorys':category,
                'categoryProgressResults':category_results
                }
        # data = {}
    return render(request,'users/dashboard.html',data)




def get_questions_per_year(category_id,framework_id,subcategory_id,org_id,year,industry,language):
    print('Filter Data for {} year'.format(year))
    sql_query ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={} or year is null) and (organisation_id={} or organisation_id is null) and 
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        data = cursor.fetchall()
        query = Q()
        if data!=[]:
            for i in data:
                query |= Q(id=i[0])
            #print('Query is ',query)
        else:
            query |= Q(id=-1)
    return query


def get_answers_per_year(category_id,framework_id,subcategory_id,org_id,year,status,industry,language):
    print('Filter Data for {} year'.format(year))
    sql_query_all ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={} or year is null) and (organisation_id={} or organisation_id is null) and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)

    sql_query_attempted ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,status,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={} or year is null) and (organisation_id={} or organisation_id is null) and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1 and status = 'OK'
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)

    sql_query_not_attempted ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,status,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={} or year is null) and (organisation_id={} or organisation_id is null) and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1  and status = 'NA'
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)

    sql_query_optional ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={} or year is null) and (organisation_id={} or organisation_id is null) and (optional = true) and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)

    if status == "All":
        sql_query=sql_query_all
    elif status == "Attempted":
        sql_query=sql_query_attempted
    elif status == "Not Attempted":
        print()
        sql_query=sql_query_not_attempted
    elif status == "Not Applicable":
        sql_query=sql_query_optional
    else:
        print('Nothing Choosen..')
        sql_query=sql_query_all

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        data = cursor.fetchall()
        query = Q()
        if data!=[]:
            for i in data:
                query |= Q(id=i[0])
            #print('Query is ',query)
        else:
            query |= Q(id=-1)
    return query

def get_answers_per_year_goal(category_id,framework_id,subcategory_id,org_id,year,industry,language):
    print('Filter Data for {} year'.format(year))

    sql_query_goal ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={} or year is null) and (organisation_id={} or organisation_id is null) and (set_goal = true) and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)



    sql_query=sql_query_goal

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        data = cursor.fetchall()
        query = Q()
        if data!=[]:
            for i in data:
                query |= Q(id=i[0])
            #print('Query is ',query)
        else:
            query |= Q(id=-1)
    return query

def get_answers_per_year_report(category_id,framework_id,subcategory_id,org_id,year,industry,language):
    print('Filter Data for {} year'.format(year))

    sql_query_goal ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        ( SELECT *
        FROM 
        (select id,question_id,organisation_id,
        ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id from questions_answer
        where (year={}) and (organisation_id={} or organisation_id is null)  and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,year,org_id,industry,language)



    sql_query=sql_query_goal

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        data = cursor.fetchall()
        query = Q()
        if data!=[]:
            for i in data:
                query |= Q(id=i[0])
            #print('Query is ',query)
        else:
            query |= Q(id=-1)
    return query



def get_questions(category_id,framework_id,subcategory_id,org_id,industry,language):
    print('Filter Data for {} Organization'.format(org_id))
    sql_query ='''
        select b.id from (
        select ques_map_id from questions_questioncategorymapping 
        where cate_id = 
        ( select id from questions_categorymapping 
        where category_id = {} and framework_id = {}and sub_category_id = {} )) a
        inner join
        (select * from
        ( SELECT id,question_id,ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY organisation_id) AS row_id
        FROM questions_answer where (organisation_id={} or organisation_id is null) and
        (question_id in (select id from questions_question where industry = '{}' and language ='{}'))
        ) c
        where row_id = 1
        ) b
        on a.ques_map_id = b.question_id
            '''.format(category_id,framework_id,subcategory_id,org_id,industry,language)

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        data = cursor.fetchall()
        query = Q()
        # print(data)
        if data!=[]:
            for i in data:
                query |= Q(id=i[0])
            #print('Query is ',query)
        else:
            query |= Q(id=-1)
    return query


@login_required(login_url="/user-login")
def add_data(request):
    print('Choosen Language...................',get_user_language())
    if request.method == 'POST':
        filter_form = AddDataForm(request.POST)
        questionForm = QuestionAnswerForm(request.POST)
        print(filter_form.is_valid(),questionForm.is_valid())
        #answer = QuestionAnswerForm(request.POST)
        if filter_form.is_valid() and questionForm.is_valid():
            print("FORM FRAMEWORk",filter_form.cleaned_data['framework'])
            if filter_form.cleaned_data['framework'] is None:
                filter_options = request.session.get('filter_form')
            else:
                try:
                    # Stroing Session if filter form is valid
                    filter_options = filter_form.cleaned_data
                    print("Checking data---->",filter_options['framework'],filter_options['category'], filter_options['sub_category'])
                    filter_options['framework']=filter_options['framework'].id
                    filter_options['category']=filter_options['category'].id
                    filter_options['sub_category']=filter_options['sub_category'].id
                    print(filter_options)
                    request.session['filter_form'] = filter_options
                    print('Current Filter Form session: ',request.session.get('filter_form'))
                except Exception as e:
                    print("Error---->",e)
                    messages.warning(request, f'Select Valid Options..')
                    filter_options = request.session.get('filter_form')
                ###############################################################################

            #Get Id's for category, framework, sub_category
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            req_year = filter_options.get('year')
            #print('filter_data',req_category,req_framework,req_subcategory,req_year,request.user.tenant.id)
            questions = Answer.objects.filter(get_questions_per_year(req_category,req_framework,req_subcategory,request.user.tenant.id,req_year,request.user.industry,get_user_language())).order_by('question')
            #print(questions)
            data = {
                    'questions':questions,
                    'form':AddDataForm(initial=request.session.get('filter_form')),
                    'questionForm':questionForm
                    }
            print('Rendering Template')
            return render(request,'users/add_data.html',data)
        else:
            print(filter_form.errors)
            if not filter_form.is_valid():
                print('form Not Valid',request.session.get('filter_form'))
                filter_form = request.session.get('filter_form')
                req_framework = filter_form.get('framework')
                req_category = filter_form.get('category')
                req_subcategory = filter_form.get('sub_category')
                req_cates_mapping = CategoryMapping.objects.get(framework=req_framework,category=req_category,sub_category=req_subcategory)
                questions = QuestionCategoryMapping.objects.filter(cate=req_cates_mapping).order_by('ques_map')
                #FrameWork Progress Counts 
                print(questionForm.cleaned_data)
                data = {
                        'questions':questions,
                        'form':filter_form,
                        'questionForm':questionForm
                    
                        }
                return render(request,'users/add_data.html',data)
            else:
                print('Question Form Errors')
                print(questionForm.errors)
                return redirect('add-data')
    else:
        form = AddDataForm()
        questionForm = QuestionAnswerForm()
        question_filter_data = request.session.get('filter_form')
        # if question_filter_data!=None:
        #     req_category=question_filter_data['category']
        #     req_framework=question_filter_data['framework']
        #     req_subcategory=question_filter_data['sub_category']
        #     req_year = question_filter_data['year']
        #questions = Answer.objects.filter(get_questions_per_year(req_category,req_framework,req_subcategory,request.user.tenant.id,req_year,request.user.industry,get_user_language())).order_by('question')
        questions=[]
        data = {
                'form':form,
                'questionForm':questionForm,
                'questions':questions,
             
                }
    return render(request,'users/add_data.html',data)

@login_required(login_url="/user-login")
def data_status(request):
    if request.method == 'POST':
        data_status_form = DataStatusForm(request.POST)
        if data_status_form.is_valid():
            if data_status_form.cleaned_data['framework'] is None:
                filter_options = request.session.get('data_status_form')
            else:
                # Stroing Session if filter form is valid
                try:
                    filter_options = data_status_form.cleaned_data
                    filter_options['framework']=filter_options['framework'].id
                    filter_options['category']=filter_options['category'].id
                    filter_options['sub_category']=filter_options['sub_category'].id
                    print(filter_options)
                    request.session['data_status_form'] = filter_options
                    print('Current Data status Form session: ',request.session.get('data_status_form'))
                except:
                    messages.warning(request, f'Select Valid Options..')
                    filter_options = request.session.get('data_status_form')
                ###############################################################################
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            req_year = filter_options.get('year')
            req_status = filter_options.get('status')
            print('Data status filter for ',req_year,req_status)
            answers = Answer.objects.filter(get_answers_per_year(req_category,req_framework,req_subcategory,request.user.tenant.id,req_year,req_status,request.user.industry,get_user_language())).order_by('question')
            data={
                'form':DataStatusForm(initial=request.session.get('data_status_form')),
                'answers':answers
            }
    else:
        print('Current Data status Form session: ',request.session.get('data_status_form'))
        form = DataStatusForm(initial=request.session.get('data_status_form'))
        if request.session.get('data_status_form') is None:
            answers = []
        else:
            filter_options = request.session.get('data_status_form')
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            req_year = filter_options.get('year')
            req_status = filter_options.get('status')
            print('Data status filter for ',req_year,req_status)
            answers = Answer.objects.filter(get_answers_per_year(req_category,req_framework,req_subcategory,request.user.tenant.id,req_year,req_status,request.user.industry,get_user_language())).order_by('question')
           
        data = {
                'form':form,
                'answers':answers             
                }
    return render(request,'users/status.html',data)


@login_required(login_url="/user-login")
def save_answer(request,id):
    if request.method == 'POST':
        answers = request.POST
        year = request.session.get('filter_form')['year']
        print('--------------------- Attempting for Year {} ---------'.format(year))
        print(answers,year)
        #questionForm = QuestionAnswerForm()
        if Answer.objects.filter(question = id , organisation=request.user.tenant.id,year = year).exists():
            current_answer = Answer.objects.get(question = id , organisation=request.user.tenant.id,year = year)
            current_answer.value = answers['value']
            current_answer.comment = answers['comment']
            current_answer.optional = "optional" in answers
            current_answer.set_goal = "setgoal" in answers
            current_answer.user = request.user
            print(current_answer.set_goal)
            current_answer.save()
            print(current_answer.value,current_answer.comment,current_answer.optional)
            print('Updated Answered for ',current_answer.question.question)
            messages.success(request, f'Answer Updated Success Fully..')
            try:
                current_answer.save()
            except Exception as e:
                print(e)

            
        else:
            question_id = Question.objects.get(id =id)
            tenant_id = Tenant.objects.get(id =request.user.tenant.id)

            new_answer = Answer(
                question = question_id,
                organisation = tenant_id,
                user = request.user,
                value = answers['value'],
                status = 'OK',
                year = year,
                comment = answers['comment'],
                optional = "optional" in answers
            )
            print('Answered for ',question_id.question)
            #print(new_answer.value,new_answer.comment,new_answer.optional)
            new_answer.save()
            messages.success(request, f'Answer Saved Success Fully..')
        return redirect('add-data')
    else:
        return redirect('add-data')


@login_required(login_url="/user-login")
def save_answer_goal(request, id):
    if request.method == 'POST':
        answers = request.POST
        year = request.session.get('data_status_form_1')['year']
        #year = int(answers.question-year)
        print('--------------------- Attempting for Year {} ---------'.format(year))
        print(answers, year)
        # questionForm = QuestionAnswerForm()
        if Answer.objects.filter(question=id, organisation=request.user.tenant.id, year=year).exists():
            current_answer = Answer.objects.get(question=id, organisation=request.user.tenant.id, year=year)
            current_answer.goal_answer = answers['value']
            current_answer.goal_comment = answers['comment']

            current_answer.user = request.user
            print(current_answer.set_goal)
            current_answer.save()
            print(current_answer.goal_answer, current_answer.goal_comment, current_answer.optional)
            print('Updated Answered for ', current_answer.question.question)
            messages.success(request, f'Answer Updated Success Fully..')
            try:
                current_answer.save()
            except Exception as e:
                print(e)
            


        else:
            question_id = Question.objects.get(id=id)
            tenant_id = Tenant.objects.get(id=request.user.tenant.id)

            new_answer = Answer(
                question=question_id,
                organisation=tenant_id,
                user=request.user,
                value=answers['value'],
                status='OK',
                year=year,
                comment=answers['comment'],
                optional="optional" in answers
            )
            print('Answered for ', question_id.question)
            # print(new_answer.value,new_answer.comment,new_answer.optional)
            new_answer.save()
            messages.success(request, f'Answer Saved Success Fully..')
        return redirect('goals-kpi')
    else:
        return redirect('goals-kpi')

def save_optional_answer(request,id):
    print('########################')
    print('from optional Answer ',id)
    try:
        question_id = Question.objects.get(id =id)
        tenant_id = Tenant.objects.get(id =request.user.tenant.id)
        new_answer = Answer(
            question = question_id,
            organisation = tenant_id,
            user = request.user,
            status = 'OK',
            year = datetime.now().year,
            optional = True
        )
        print('Answered for ',question_id.question)
        #print(new_answer.value,new_answer.comment,new_answer.optional)
        new_answer.save()
        messages.success(request, f'Answer Marked as Optional..')
        return redirect('todos')
    except Exception as e:
        print(e)
        messages.warning(request, f'Error Occured..')
        return redirect('todos')



@login_required(login_url="/user-login")
def review_data(request):
    if request.method == 'POST':
        filter_form = StatusForm(request.POST)
        if filter_form.is_valid():
            
            if filter_form.cleaned_data['framework'] is None:
                filter_options = request.session.get('status_filter_form')
            else:
                try:
                    # Stroing Session if filter form is valid
                    filter_options = filter_form.cleaned_data
                    filter_options['framework']=filter_options['framework'].id
                    filter_options['category']=filter_options['category'].id
                    filter_options['sub_category']=filter_options['sub_category'].id
                    print(filter_options)
                    request.session['status_filter_form'] = filter_options
                    print('Current status_filter_form session: ',request.session.get('status_filter_form'))
                    ###############################################################################
                except:
                    messages.warning(request, f'Select Valid Options..')
                    filter_options = request.session.get('status_filter_form')
            print('Valid POST If Condition')
            #Get Id's for category, framework, sub_category
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            print('filter_data',req_category,req_framework,req_subcategory,request.user.tenant.id)
            questions = Answer.objects.filter(get_questions(req_category,req_framework,req_subcategory,request.user.tenant.id,request.user.industry,get_user_language()))
            print(questions)
            data = {
                    'questions':questions,
                    'form':StatusForm(initial=request.session.get('status_filter_form'))
                    }
            print('Rendering Template')
            return render(request,'users/review_data.html',data)
        else:
            print('Valid POST else Condition')
            if not filter_form.is_valid():
                print('form Not Valid')
                filter_form = request.session.get('status_filter_form')
                req_framework = filter_form.get('framework')
                req_category = filter_form.get('category')
                req_subcategory = filter_form.get('sub_category')
                req_cates_mapping = CategoryMapping.objects.get(framework=req_framework,category=req_category,sub_category=req_subcategory)
                questions = QuestionCategoryMapping.objects.filter(cate=req_cates_mapping)
                data = {
                        'questions':questions,
                        'form':filter_form
                
                        }
                return render(request,'users/review_data.html',data)
            else:
                return redirect('add-data')
    else:
        print('Get Request')
        print('Current Filter Form session: ',request.session.get('status_filter_form'))
        form = StatusForm(initial=request.session.get('status_filter_form'))
        question_filter_data = request.session.get('status_filter_form')
        if question_filter_data!=None:
            print('Get If Condition')
            req_category=question_filter_data['category']
            req_framework=question_filter_data['framework']
            req_subcategory=question_filter_data['sub_category']
            questions = Answer.objects.filter(get_questions(req_category,req_framework,req_subcategory,request.user.tenant.id,request.user.industry,get_user_language()))
        else:
            print('Get Else Condition')
            questions=[]
        data = {
                'form':form,
                'questions':questions,
             
                }
    return render(request,'users/review_data.html',data)

def display_data(request,id):
    isNumber = False
    print('displaying data for '.format(id))
    question = Answer.objects.filter(question = id)[0]
    print(question.question.question)
    data = Answer.objects.filter(question = id).values_list('value','year')
    values=[]
    years=[]
    data_dict=dict()
    chart_color="rgb({},{},{})".format(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    for i in data:
        if i[0]==None or i[1]==None:
            continue
        else:
            try:
                data_dict[int(i[1])]=int(i[0])
                isNumber = True
            except:
                values.append(i[0])
                years.append(int(i[1]))
    if isNumber:
        for i in range(min(data_dict),max(data_dict)+1):
            if i in data_dict:
                values.append(data_dict[i])
                years.append(i)
            else:
                values.append(0)
                years.append(i)

    answers = zip(years, values)
    print(answers)
    print(years,values,chart_color)
    data = {
        'question':question,
        'years':years,
        'values':values,
        'chart_color':chart_color,
        'isNumber':isNumber,
        'answers':answers
        }
    return render(request,'users/display_data.html',data)


def report_pdf_view(request):

    sales = [
        {"item": "Keyboard", "amount": "$120,00"},
        {"item": "Mouse", "amount": "$10,00"},
        {"item": "House", "amount": "$1 000 000,00"},
    ]
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('courier', 'B', 16)
    pdf.cell(40, 10, 'This is what you have sold this month so far:', 0, 1)
    pdf.cell(40, 10, '', 0, 1)
    pdf.set_font('courier', '', 12)
    pdf.cell(200, 8, f"{'Item'.ljust(30)} {'Amount'.rjust(20)}", 0, 1)
    pdf.line(10, 30, 150, 30)
    pdf.line(10, 38, 150, 38)
    for line in sales:
        pdf.cell(200, 8, f"{line['item'].ljust(30)} {line['amount'].rjust(20)}", 0, 1)

    pdf.output('tuto1.pdf', 'F')
    return redirect('report')


@login_required(login_url="/user-login")
def report(request):

    # basic_data_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Basic Data").count()
    # environmental_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Environmental").count()
    # social_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Social").count()
    # governance_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Governance").count()
    # data = {'basic_data':basic_data_count,'environmental':environmental_count,'social':social_count,'governance':governance_count}
    data = {}
    from datetime import date
    todays_date = date.today()
    current_year = todays_date.year
    print(current_year)
    form = StatusForm1(initial=request.session.get('data_status_form_1'))
    # answers = Answer.objects.filter(
    #     get_answers_per_year_goal(req_category, req_framework, req_subcategory, request.user.tenant.id, req_year,
    #                               request.user.industry)).order_by('question')
    data['form'] = form

    if request.method == 'POST':
        data_status_form = StatusForm1(request.POST)
        if data_status_form.is_valid():
            if data_status_form.cleaned_data['framework'] is None:
                filter_options = request.session.get('data_status_form_1')
            else:
                # Stroing Session if filter form is valid
                try:
                    filter_options = data_status_form.cleaned_data
                    filter_options['framework'] = filter_options['framework'].id
                    filter_options['category'] = filter_options['category'].id
                    filter_options['sub_category'] = filter_options['sub_category'].id

                    print(filter_options)
                    # filter_options['removegoal'] = filter_options['removegoal']

                    request.session['data_status_form_1'] = filter_options
                    print('Current Data status Form session: ', request.session.get('data_status_form_1'))
                except Exception as e:
                    print("INTO EXCEPTION------>", e)
                    messages.warning(request, f'Select Valid Options..')
                    filter_options = request.session.get('data_status_form')
                ###############################################################################
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            req_year = filter_options.get('year')
            print('Data status filter for ', req_year)
            answers = Answer.objects.filter(
                get_answers_per_year_report(req_category, req_framework, req_subcategory, request.user.tenant.id,
                                          req_year,
                                          request.user.industry,get_user_language())).order_by('question')
        report_list = []
        for answer in answers:
            #report_list.append({"question": answer.question.question, "answer": answer.value})
            report_list.append([answer.question.question, answer.value,answer.comment])
            print("answer------>",answer.question.id)
        print(report_list)

        try:
            import pandas
            df = pandas.DataFrame(report_list, columns=["Question", "Answer", "Comment"])
            df.to_csv("static/report.csv")
            # pdf = FPDF('P', 'mm', 'A4')
            # pdf.add_page()
            # pdf.set_font('courier', 'B', 16)
            # pdf.cell(40, 10, 'REPORT For Current year:', 0, 1)
            # pdf.cell(40, 10, '', 0, 1)
            # pdf.set_font('courier', '', 12)
            # pdf.cell(200, 8, f"{'Item'.ljust(30)} {'Amount'.rjust(20)}", 0, 1)
            # pdf.line(10, 30, 150, 30)
            # pdf.line(10, 38, 150, 38)
            #
            # # for line in report_list:
            # #     #pdf.cell(200, 8, f"{line['item'].ljust(30)} {line['amount'].rjust(20)}", 0, 1)
            # #     pdf.cell(200,8, f"{line['question'].ljust(30)} {line['answer'].rjust(20)}" )
            #
            # th = pdf.font_size
            # epw = pdf.w - 2 * pdf.l_margin
            # col_width = epw
            # pdf.ln(4 * th)
            #
            # pdf.set_font('Times', 'B', 14.0)
            # pdf.cell(epw, 0.0, 'With more padding', align='C')
            # pdf.set_font('Times', '', 10.0)
            # pdf.ln(0.5)
            #
            # for row in report_list:
            #     for datum in row:
            #         # Enter data in colums
            #         pdf.cell(col_width, 2 * th, str(datum), border=1)
            #         #pdf.cell(2.0, 0.15, str(datum), align='C', border=1)  ## width = 2.0
            #     pdf.ln(2 * th)

            #pdf.output('report.pdf', 'F')
            return FileResponse(open('static/report.csv', 'rb'), as_attachment=True, content_type='application/pdf')

        except Exception as e:
            print("ERROR ---->", e)
            data["message"] = "Cannot Generate report"

        data['questions'] = answers
        data['form'] = data_status_form
        return render(request, 'users/goals_kpi.html', data)
    return render(request,'users/report.html',data)

@login_required(login_url="/user-login")
def remove_goal(request, goal_id):
    answer = Answer.objects.get(id=goal_id)
    answer.set_goal = False
    answer.save()
    print("----here--->",answer)
    return redirect('goals-kpi')


@login_required(login_url="/user-login")
def goals_and_kpi(request):
    #basic_data_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Basic Data").count()
    #environmental_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Environmental").count()
    #social_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Social").count()
    #governance_count = QuestionCategoryMapping.objects.filter(cate__sub_category__name__contains="Governance").count()
    form = StatusForm1(initial=request.session.get('data_status_form_1'))
    data = {'form':form}
    if request.session.get('data_status_form') is None:
        answers = []
    else:
        filter_options = request.session.get('data_status_form')
        req_framework = filter_options.get('framework')
        req_category = filter_options.get('category')
        req_subcategory = filter_options.get('sub_category')
        req_year = filter_options.get('year')
        req_status = filter_options.get('status')
        print('Data status filter for ', req_year, req_status)
        answers = Answer.objects.filter(
            get_answers_per_year_goal(req_category, req_framework, req_subcategory, request.user.tenant.id, req_year,
                                 request.user.industry,get_user_language())).order_by('question')
        data['questions'] = answers
        data['form'] = form

    #data = {'basic_data':basic_data_count,'environmental':environmental_count,'social':social_count,'governance':governance_count}
    if request.method == 'POST':
        data_status_form = StatusForm1(request.POST)
        if data_status_form.is_valid():
            if data_status_form.cleaned_data['framework'] is None:
                filter_options = request.session.get('data_status_form_1')
            else:
                # Stroing Session if filter form is valid
                try:
                    filter_options = data_status_form.cleaned_data
                    filter_options['framework'] = filter_options['framework'].id
                    filter_options['category'] = filter_options['category'].id
                    filter_options['sub_category'] = filter_options['sub_category'].id
                    
                    print(filter_options)
                    # filter_options['removegoal'] = filter_options['removegoal']

                    request.session['data_status_form_1'] = filter_options
                    print('Current Data status Form session: ', request.session.get('data_status_form_1'))
                except Exception as e:
                    print("INTO EXCEPTION------>", e)
                    messages.warning(request, f'Select Valid Options..')
                    filter_options = request.session.get('data_status_form')
                ###############################################################################
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            req_year = filter_options.get('year')
            print('Data status filter for ', req_year)
            answers = Answer.objects.filter(
                get_answers_per_year_goal(req_category, req_framework, req_subcategory, request.user.tenant.id, req_year,
                                      request.user.industry,get_user_language())).order_by('question')


        data['questions'] = answers
        data['form'] = data_status_form
        return render(request, 'users/goals_kpi.html',data )
    return render(request,'users/goals_kpi.html',data )

@login_required(login_url="/user-login")
def todos(request):
    if request.method == 'POST':
        todo_form = TodoForm(request.POST)
        if todo_form.is_valid():
            if todo_form.cleaned_data['framework'] is None:
                filter_options = request.session.get('todo_form')
            else:
                # Stroing Session if filter form is valid
                try:
                    filter_options = todo_form.cleaned_data
                    filter_options['framework']=filter_options['framework'].id
                    filter_options['category']=filter_options['category'].id
                    filter_options['sub_category']=filter_options['sub_category'].id
                    print(filter_options)
                    request.session['todo_form'] = filter_options
                    print('Current Data status Form session: ',request.session.get('todo_form'))
                except:
                    messages.warning(request, f'Select Valid Options..')
                    filter_options = request.session.get('todo_form')
                ###############################################################################
            req_framework = filter_options.get('framework')
            req_category = filter_options.get('category')
            req_subcategory = filter_options.get('sub_category')
            req_year = datetime.now().year
            req_status = "Not Attempted"
            print('Data status filter for ',req_year,req_status)
            answers = Answer.objects.filter(get_answers_per_year(req_category,req_framework,req_subcategory,request.user.tenant.id,req_year,req_status,request.user.industry,get_user_language())).order_by('question')
            print(answers)
            data={
                'form':TodoForm(initial=request.session.get('todo_form')),
                'answers':answers
            }
    else:
        print('Current TODO status Form session: ',request.session.get('todo_form'))
        todo_form = TodoForm(initial=request.session.get('todo_form'))
        if request.session.get('todo_form') is None:
            answers = []
        else:
            form = request.session.get('todo_form')
            req_framework = form.get('framework')
            req_category = form.get('category')
            req_subcategory = form.get('sub_category')
            req_year = datetime.now().year
            req_status = "Not Attempted"
            print('Data status filter for ',req_status)
            answers = Answer.objects.filter(get_answers_per_year(req_category,req_framework,req_subcategory,request.user.tenant.id,req_year,req_status,request.user.industry,get_user_language())).order_by('question')
        print(answers)
        data = {
                'form':todo_form,
                'answers':answers             
                }
    return render(request,'users/todos.html',data)

def single_answer_attempt(request,id):
    answer = Answer.objects.filter(Q(question=id) & Q(organisation=None))
    print(answer)
    return render(request,'users/missing_question.html',{'questions':answer})

@login_required(login_url="/user-login")
def save_single_answer(request,id):
    if request.method == 'POST':
        answers = request.POST
        year = datetime.now().year
        print('--------------------- Attempting for Year {} ---------'.format(year))
        print(answers,year)
        question_id = Question.objects.get(id =id)
        tenant_id = Tenant.objects.get(id =request.user.tenant.id)
        new_answer = Answer(
            question = question_id,
            organisation = tenant_id,
            user = request.user,
            value = answers['value'],
            status = 'OK',
            year = year,
            comment = answers['comment'],
            optional = "optional" in answers
        )
        print('Answered for ',question_id.question)
        new_answer.save()
        messages.success(request, f'Answer Saved Success Fully..')
        return redirect('todos')
    else:
        return redirect('todos')

@login_required(login_url="/user-login")
def getcategories(request):
    print('Choosen Language...................',get_user_language())
    print('Getting Categories..',request.GET)
    #print(request.GET['cnt'],request.GET['id_value'])
    framework_id = request.GET['id_value']
    print('raju..',framework_id,get_user_language())
    categories = CategoryMapping.objects.filter(Q(framework=framework_id))
    result_set=[]
    print(categories)
    for c in categories:
        print(c.category.name,c.category.id)
        if {'name': c.category.name,'id':c.category.id} not in result_set:
            result_set.append({'name': c.category.name,'id':c.category.id})
    result_set.append({'name': '---------','id':0})
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


@login_required(login_url="/user-login")
def getsubcategories(request):
    print('Getting SubCategories..',request.GET)
    print('Choosen Language...................',get_user_language())
    print('######## Sub categories ############')
    category_id = request.GET['id_value']
    framework_id = request.GET['framework']
    categories = CategoryMapping.objects.filter(Q(category=category_id) & Q(framework=framework_id))
    result_set=[]
    print(categories)
    for c in categories:
        print(c.sub_category.name,c.sub_category.id)
        if {'name': c.sub_category.name,'id':c.sub_category.id} not in result_set:
            result_set.append({'name': c.sub_category.name,'id':c.sub_category.id})
    result_set.append({'name': '---------','id':0})
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')

def progressPerFramework(org_id,year,user_language):
    query1='''
        select b.name,a.totalquestions from
            (select framework_id,count(*) totalquestions from 
            (select * from questions_categorymapping a 
            inner join 
            ( select * from questions_questioncategorymapping ) b
            on a.id = b.cate_id) b
            group by framework_id) a
            inner join
            (select name,id from questions_category where type='framework' and language='{}') b
            on a.framework_id = b.id 
    '''.format(user_language)
    query2='''    select b.name,a.totalquestions from
    (select framework_id,count(*) totalquestions from 
    (select * from questions_categorymapping a 
    inner join 
    ( 
    select * from questions_questioncategorymapping a
    inner join 
    ( select question_id from questions_answer where organisation_id={} and year = {}) b
        on b.question_id = a.ques_map_id 
    ) b
    on a.id = b.cate_id) b
    group by framework_id) a
    inner join
    (select name,id from questions_category where type='framework' and language='{}') b
    on a.framework_id = b.id'''.format(org_id,year,user_language)

    framework=[]
    questionCount=[]
    answerCount=[]
    answer_count = dict()
    with connection.cursor() as cursor:
        cursor.execute(query1)
        data = cursor.fetchall()
        for i in data:
            framework.append(i[0])
            questionCount.append(int(i[1]))
        cursor.execute(query2)
        data = cursor.fetchall()
        for i in data:
            answer_count[i[0]]=int(i[1])

    for i in framework:
        if i in answer_count:
            answerCount.append(answer_count[i])
        else:
            answerCount.append(0)
    return framework,questionCount,answerCount



def progressPerCategory(framework_id,org_id,year,user_language):
    query='''
    select name, sum(total) total, sum(score) score from (
    select b.name, a.total,a.score from (
    (select a.category_id,b.total,b.score from questions_categorymapping a 
    inner join 
    (select cate_id,count(*) total,sum(score) score from (
    select cate_id,ques_map_id, case when question_id is null then 0 else 1 end score from 
    (select cate_id,ques_map_id from questions_questioncategorymapping where cate_id in
    ( select id from questions_categorymapping where framework_id = {} )) a
    left join
    (select question_id from questions_answer where organisation_id = {} and year = {}) b
    on a.ques_map_id = b.question_id ) a
    group by cate_id) b 
    on a.id = b.cate_id)) a
    inner join 
    (select name,id from questions_category where language='{}') b
    on a.category_id=b.id) a
    group by name
    '''.format(framework_id,org_id,year,user_language)
    
    category=[]
    total=[]
    answers=[]
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        for i in data:
            category.append(i[0])
            total.append(int(i[1]))
            answers.append(int(i[2]))

    return category,total,answers

def changeLanguage(request, ln):
    print("------"+ln)
    from django.conf import settings
    
    if ln == 'en':
        from django.utils import translation
        user_language = 'en'
        translation.activate(user_language)
    elif ln == 'de':
        from django.utils import translation
        user_language = 'de'
        translation.activate(user_language)
    print("earlier-->", settings.LANGUAGE_CODE)
    settings.LANGUAGE_CODE = ln
    print("AFTER-->", settings.LANGUAGE_CODE)
    request.session['user_language'] = user_language
    return redirect('dashboard')

def changeLanguageLogin(request, ln):
    from django.conf import settings

    if ln == 'en':
        from django.utils import translation
        user_language = 'en'
        translation.activate(user_language)
        # settings.LANGUAGE_CODE = 'en'
    elif ln == 'de':
        from django.utils import translation
        user_language = 'de'
        # settings.LANGUAGE_CODE = 'de'
        translation.activate(user_language)
    print("earlier-->",settings.LANGUAGE_CODE)
    settings.LANGUAGE_CODE = ln
    print("AFTER-->",settings.LANGUAGE_CODE)

    request.session['user_language'] = user_language
    return redirect('user-login')

