from django.shortcuts import render
from django.contrib.auth.decorators import (login_required, user_passes_test)
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import Choices, Questions, Answer, Form, Responses
from django.core import serializers
import json
import random
import string
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail,  BadHeaderError
from django.conf import settings
import re
# Create your views here.


@login_required(login_url="/user-login")
def stakeholders_user(request):

    forms = Form.objects.filter(creator__tenant=request.user.tenant)
    context = {"forms": forms}
    # return render(request, "index/index.html", {
    #     "forms": forms
    # })
    return render(request, 'stakeholder/stakeholder.html', context)


@login_required(login_url="/user-login")
def send_form_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        link = request.POST.get('link')
        email = email.split(';')
        EMAIL_REGEX = re.compile('[\w\.-]+@[\w\.-]+(\.[\w]+)+')
        correct_email = []
        for e in range(0,len(email)):
            email[e] = email[e].strip()
            if EMAIL_REGEX.match(email[e]):
                correct_email.append(email[e])

        link_code = link.split("/")[2]

        print("send form link ------->", email, link)
        subject = "Survey Link"
        current_site = get_current_site(request)
        message = "Please fill out this Survey form-> \n LINK : {protocol}://{link}".format(link=link, protocol=settings.PROTOCOL)
        # message = render_to_string('<h1>Please fill out this form</h1><a href={link}>Survey form</a>'.format(link=link))

        print('Sending Mail..')
        try:
            send_mail(subject,from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=correct_email, fail_silently=False, message=message)
            # print(message)
            print('Mail sent..')
        except BadHeaderError:
            print("ERROR")
            #messages.error(request, 'Invalid header found.')

    return redirect('edit_form', code=link_code)


def create_form(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        data = json.loads(request.body)
        title = data["title"]
        code = ''.join(random.choice(string.ascii_letters + string.digits)
                       for x in range(30))
        choices = Choices(choice="Option 1")
        choices.save()
        question = Questions(question_type="multiple choice",
                             question="Untitled Question", required=False)
        question.save()
        question.choices.add(choices)
        question.save()
        form = Form(code=code, title=title, creator=request.user)
        form.save()
        form.questions.add(question)
        form.save()
        return JsonResponse({"message": "Sucess", "code": code})


def edit_form(request, code):

    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    return render(request, "stakeholder/form.html", {
        "code": code,
        "form": formInfo
    })


def edit_title(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        if len(data["title"]) > 0:
            formInfo.title = data["title"]
            formInfo.save()
        else:
            formInfo.title = formInfo.title[0]
            formInfo.save()
        return JsonResponse({"message": "Success", "title": formInfo.title})


def edit_description(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.description = data["description"]
        formInfo.save()
        return JsonResponse({"message": "Success", "description": formInfo.description})


def edit_setting(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.collect_email = data["collect_email"]
        formInfo.authenticated_responder = data["authenticated_responder"]
        formInfo.confirmation_message = data["confirmation_message"]
        formInfo.edit_after_submit = data["edit_after_submit"]
        formInfo.save()
        return JsonResponse({'message': "Success"})


def delete_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        # Delete all questions and choices
        for i in formInfo.questions.all():
            for j in i.choices.all():
                j.delete()
            i.delete()
        for i in Responses.objects.filter(response_to=formInfo):
            for j in i.response.all():
                j.delete()
            i.delete()
        formInfo.delete()
        return JsonResponse({'message': "Success"})


def edit_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = data["id"]
        question = Questions.objects.filter(id=question_id)
        if question.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else:
            question = question[0]
        question.question = data["question"]
        question.question_type = data["question_type"]
        question.required = data["required"]
        question.save()
        return JsonResponse({'message': "Success"})


def edit_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice_id = data["id"]
        choice = Choices.objects.filter(id=choice_id)
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else:
            choice = choice[0]
        choice.choice = data["choice"]
        if(data.get('is_answer')):
            choice.is_answer = data["is_answer"]
        choice.save()
        return JsonResponse({'message': "Success"})


def add_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice = Choices(choice="Option")
        choice.save()
        formInfo.questions.get(pk=data["question"]).choices.add(choice)
        formInfo.save()
        return JsonResponse({"message": "Success", "choice": choice.choice, "id": choice.id})


def remove_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice = Choices.objects.filter(pk=data["id"])
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else:
            choice = choice[0]
        choice.delete()
        return JsonResponse({"message": "Success"})


def get_choice(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "GET":
        question = Questions.objects.filter(id=question)
        if question.count() == 0:
            return HttpResponseRedirect(reverse('404'))
        else:
            question = question[0]
        choices = question.choices.all()
        choices = [{"choice": i.choice, "is_answer": i.is_answer, "id": i.id}
                   for i in choices]
        return JsonResponse({"choices": choices, "question": question.question, "question_type": question.question_type, "question_id": question.id})


def add_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        choices = Choices(choice="Option 1")
        choices.save()
        question = Questions(question_type="multiple choice",
                             question="Untitled Question", required=False)
        question.save()
        question.choices.add(choices)
        question.save()
        formInfo.questions.add(question)
        formInfo.save()
        return JsonResponse({'question': {'question': "Untitled Question", "question_type": "multiple choice", "required": False, "id": question.id},
                             "choices": {"choice": "Option 1", "is_answer": False, 'id': choices.id}})


def delete_question(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        question = Questions.objects.filter(id=question)
        if question.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else:
            question = question[0]
        for i in question.choices.all():
            i.delete()
            question.delete()
        return JsonResponse({"message": "Success"})


def score(request, code):
    data = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.get(code=code)
    responseInfo = Responses.objects.filter(response_to=formInfo)
    #print(responseInfo)
    answers_objects = []
    form_question = formInfo.questions
    mcq = {}
    checkbox = {}
    for question in form_question.all():
        CHOICES = {}
        print(question.question_type)
        if question.question_type == "multiple choice":

            for choice in question.choices.all():
                CHOICES[choice.id] = {"Name": choice.choice , "score": 0}
            mcq[question.id] = {"name": question.question , "choices":CHOICES }
        elif question.question_type == "checkbox":
            for choice in question.choices.all():
                CHOICES[choice.id] = {"Name": choice.choice , "score": 0}
            checkbox[question.id] = {"name": question.question , "choices":CHOICES }


    #print(mcq)
    #print(checkbox)


    for res in responseInfo:
        for res2 in res.response.all():
            #print(res2)

            if res2.answer_to.id in mcq.keys():

                mcq[res2.answer_to.id]['choices'][int(res2.answer)]['score'] += 1

            elif res2.answer_to.id in checkbox.keys():
                checkbox[res2.answer_to.id]['choices'][int(res2.answer)]['score'] += 1
    #print(checkbox)
    #print(mcq)
    final_mcq_list = []
    for key, values in mcq.items():
        #print(key, values)
        name =values['name']
        labels = []
        scores = []
        for key2, values2 in values['choices'].items():
            #print(key2, values2)
            labels.append(values2['Name'])
            scores.append(values2['score'])
        final_mcq_list.append({"question": {"key": key, "name": name, "label":labels, "scores":scores}})
    #print(final_mcq_list)
    data['mcq'] = final_mcq_list

    final_checkbox_list =[]
    for key, values in checkbox.items():
        #print(key, values)
        name =values['name']
        labels = []
        scores = []
        for key2, values2 in values['choices'].items():
            #print(key2, values2)
            labels.append(values2['Name'])
            scores.append(values2['score'])
        final_checkbox_list.append({"question": {"key": key, "name": name, "label":labels, "scores":scores}})
    print(final_checkbox_list)
    data['checkbox'] = final_checkbox_list

         #answers_objects.append(res.response.all())
    #
    # for answers in answers_objects:
    #     print(answers.answer)
    # Checking if form exists
    # if formInfo.count() == 0:
    #     return HttpResponseRedirect(reverse('404'))
    # else:
    #     formInfo = formInfo[0]
    # # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    else:
        data['form'] = formInfo
        return render(request, "stakeholder/score.html", data)


def edit_score(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args=[code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question_id = data["question_id"]
            question = formInfo.questions.filter(id=question_id)
            if question.count() == 0:
                return HttpResponseRedirect(reverse("edit_form", args=[code]))
            else:
                question = question[0]
            score = data["score"]
            if score == "":
                score = 0
            question.score = score
            question.save()
            return JsonResponse({"message": "Success"})


def feedback(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args=[code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question = formInfo.questions.get(id=data["question_id"])
            question.feedback = data["feedback"]
            question.save()
            return JsonResponse({'message': "Success"})


def view_form(request, code):
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
    return render(request, "stakeholder/view_form.html", {
        "form": formInfo
    })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def submit_form(request, code):
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits)
                       for x in range(20))
        if formInfo.authenticated_responder:
            response = Responses(response_code=code, response_to=formInfo,
                                 responder_ip=get_client_ip(request), responder=request.user)
            response.save()
        else:
            if not formInfo.collect_email:
                response = Responses(
                    response_code=code, response_to=formInfo, responder_ip=get_client_ip(request))
                response.save()
            else:
                response = Responses(response_code=code, response_to=formInfo, responder_ip=get_client_ip(
                    request), responder_email=request.POST["email-address"])
                response.save()
        for i in request.POST:
            # Excluding csrf token
            if i == "csrfmiddlewaretoken" or i == "email-address":
                continue
            question = formInfo.questions.get(id=i)
            for j in request.POST.getlist(i):
                answer = Answer(answer=j, answer_to=question)
                answer.save()
                response.response.add(answer)
                response.save()
        return render(request, "stakeholder/form_response.html", {
            "form": formInfo,
            "code": code
        })


def responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    return render(request, "stakeholder/responses.html", {
        "form": formInfo,
        "responses": Responses.objects.filter(response_to=formInfo)
    })


def response(request, code, response_code):
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    # if not formInfo.allow_view_score:
    #     if formInfo.creator != request.user:
    #         return HttpResponseRedirect(reverse("403"))
    total_score = 0
    score = 0
    responseInfo = Responses.objects.filter(response_code=response_code)
    if responseInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        responseInfo = responseInfo[0]
    return render(request, "stakeholder/response.html", {
        "form": formInfo,
        "response": responseInfo,
        "score": score,
        "total_score": total_score
    })


def edit_response(request, code, response_code):
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    response = Responses.objects.filter(
        response_code=response_code, response_to=formInfo)
    if response.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        response = response[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        if response.responder != request.user:
            return HttpResponseRedirect(reverse('403'))
    if request.method == "POST":
        if formInfo.authenticated_responder and not response.responder:
            response.responder = request.user
            response.save()
        if formInfo.collect_email:
            response.responder_email = request.POST["email-address"]
            response.save()
        # Deleting all existing answers
        for i in response.response.all():
            i.delete()
        for i in request.POST:
            # Excluding csrf token and email address
            if i == "csrfmiddlewaretoken" or i == "email-address":
                continue
            question = formInfo.questions.get(id=i)
            for j in request.POST.getlist(i):
                answer = Answer(answer=j, answer_to=question)
                answer.save()
                response.response.add(answer)
                response.save()

        return render(request, "stakeholder/form_response.html", {
            "form": formInfo,
            "code": response.response_code
        })

    return render(request, "stakeholder/edit_response.html", {
        "form": formInfo,
        "response": response
    })


def contact_form_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits)
                       for x in range(30))
        name = Questions(question_type="short", question="Name", required=True)
        name.save()
        email = Questions(question_type="short",
                          question="Email", required=True)
        email.save()
        address = Questions(question_type="paragraph",
                            question="Address", required=True)
        address.save()
        phone = Questions(question_type="short",
                          question="Phone number", required=False)
        phone.save()
        comments = Questions(question_type="paragraph",
                             question="Comments", required=False)
        comments.save()
        form = Form(code=code, title="Contact information", creator=request.user,
                    background_color="#e2eee0", allow_view_score=False, edit_after_submit=True)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(address)
        form.questions.add(phone)
        form.questions.add(comments)
        form.save()
        return JsonResponse({"message": "Sucess", "code": code})


def customer_feedback_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits)
                       for x in range(30))
        comment = Choices(choice="Comments")
        comment.save()
        question = Choices(choice="Questions")
        question.save()
        bug = Choices(choice="Bug Reports")
        bug.save()
        feature = Choices(choice="Feature Request")
        feature.save()
        feedback_type = Questions(
            question="Feedback Type", question_type="multiple choice", required=False)
        feedback_type.save()
        feedback_type.choices.add(comment)
        feedback_type.choices.add(bug)
        feedback_type.choices.add(question)
        feedback_type.choices.add(feature)
        feedback_type.save()
        feedback = Questions(question="Feedback",
                             question_type="paragraph", required=True)
        feedback.save()
        suggestion = Questions(
            question="Suggestions for improvement", question_type="paragraph", required=False)
        suggestion.save()
        name = Questions(
            question="Name", question_type="short", required=False)
        name.save()
        email = Questions(question="Email",
                          question_type="short", required=False)
        email.save()
        form = Form(code=code, title="Customer Feedback", creator=request.user, background_color="#e2eee0", confirmation_message="Thanks so much for giving us feedback!",
                    description="We would love to hear your thoughts or feedback on how we can improve your experience!", allow_view_score=False, edit_after_submit=True)
        form.save()
        form.questions.add(feedback_type)
        form.questions.add(feedback)
        form.questions.add(suggestion)
        form.questions.add(name)
        form.questions.add(email)
        return JsonResponse({"message": "Sucess", "code": code})


def event_registration_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits)
                       for x in range(30))
        name = Questions(
            question="Name", question_type="short", required=False)
        name.save()
        email = Questions(question="email",
                          question_type="short", required=True)
        email.save()
        organization = Questions(
            question="Organization", question_type="short", required=True)
        organization.save()
        day1 = Choices(choice="Day 1")
        day1.save()
        day2 = Choices(choice="Day 2")
        day2.save()
        day3 = Choices(choice="Day 3")
        day3.save()
        day = Questions(question="What days will you attend?",
                        question_type="checkbox", required=True)
        day.save()
        day.choices.add(day1)
        day.choices.add(day2)
        day.choices.add(day3)
        day.save()
        dietary_none = Choices(choice="None")
        dietary_none.save()
        dietary_vegetarian = Choices(choice="Vegetarian")
        dietary_vegetarian.save()
        dietary_kosher = Choices(choice="Kosher")
        dietary_kosher.save()
        dietary_gluten = Choices(choice="Gluten-free")
        dietary_gluten.save()
        dietary = Questions(question="Dietary restrictions",
                            question_type="multiple choice", required=True)
        dietary.save()
        dietary.choices.add(dietary_none)
        dietary.choices.add(dietary_vegetarian)
        dietary.choices.add(dietary_gluten)
        dietary.choices.add(dietary_kosher)
        dietary.save()
        accept_agreement = Choices(choice="Yes")
        accept_agreement.save()
        agreement = Questions(
            question="I understand that I will have to pay $$ upon arrival", question_type="checkbox", required=True)
        agreement.save()
        agreement.choices.add(accept_agreement)
        agreement.save()
        form = Form(code=code, title="Event Registration", creator=request.user, background_color="#fdefc3",
                    confirmation_message="We have received your registration.\n\
Insert other information here.\n\
\n\
Save the link below, which can be used to edit your registration up until the registration closing date.",
                    description="Event Timing: January 4th-6th, 2016\n\
Event Address: 123 Your Street Your City, ST 12345\n\
Contact us at (123) 456-7890 or no_reply@example.com", edit_after_submit=True, allow_view_score=False)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(organization)
        form.questions.add(day)
        form.questions.add(dietary)
        form.questions.add(agreement)
        form.save()
        return JsonResponse({"message": "Sucess", "code": code})


def delete_responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    # Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        formInfo = formInfo[0]
    # Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        responses = Responses.objects.filter(response_to=formInfo)
        for response in responses:
            for i in response.response.all():
                i.delete()
            response.delete()
        return JsonResponse({"message": "Success"})

# Error handler


def FourZeroThree(request):
    return render(request, "error/403.html")


def FourZeroFour(request):
    return render(request, "error/404.html")
