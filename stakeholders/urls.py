from django.urls import path
from . import views

urlpatterns = [
    path("stakeholders/", views.stakeholders_user, name="stakeholders1"),
    path('stakeholders/form/create', views.create_form, name="create_form"),
    path('stakeholders/form/create/contact',
         views.contact_form_template, name="contact_form_template"),
    path('stakeholders/form/create/feedback',
         views.customer_feedback_template, name="customer_feedback_template"),
    path('stakeholders/form/create/event',
         views.event_registration_template, name="event_registration_template"),
    path('stakeholders/form/<str:code>/edit',
         views.edit_form, name="edit_form"),
    path('stakeholders/form/<str:code>/edit_title',
         views.edit_title, name="edit_title"),
    path('stakeholders/form/<str:code>/edit_description',
         views.edit_description, name="edit_description"),
    path('stakeholders/form/<str:code>/edit_setting',
         views.edit_setting, name="edit_setting"),
    path('stakeholders/form/<str:code>/delete',
         views.delete_form, name="delete_form"),
    path('stakeholders/form/<str:code>/edit_question',
         views.edit_question, name="edit_question"),
    path('stakeholders/form/<str:code>/edit_choice',
         views.edit_choice, name="edit_choice"),
    path('stakeholders/form/<str:code>/add_choice',
         views.add_choice, name="add_choice"),
    path('stakeholders/form/<str:code>/remove_choice',
         views.remove_choice, name="remove_choice"),
    path('stakeholders/form/<str:code>/get_choice/<str:question>',
         views.get_choice, name="get_choice"),
    path('stakeholders/form/<str:code>/add_question',
         views.add_question, name="add_question"),
    path('stakeholders/form/<str:code>/delete_question/<str:question>',
         views.delete_question, name="delete_question"),
    path('stakeholders/form/<str:code>/score', views.score, name="score"),
    path('stakeholders/form/<str:code>/edit_score',
         views.edit_score, name="edit_score"),
    path('stakeholders/form/<str:code>/feedback',
         views.feedback, name="feedback"),
    path('stakeholders/form/<str:code>/viewform',
         views.view_form, name="view_form"),
    path('form/<str:code>/viewform', views.view_form, name="view_form1"),
    path('stakeholders/form/<str:code>/submit',
         views.submit_form, name="submit_form"),
    path('stakeholders/form/<str:code>/responses',
         views.responses, name='responses'),
    path('stakeholders/form/<str:code>/response/<str:response_code>',
         views.response, name="response"),
    path('stakeholders/form/<str:code>/response/<str:response_code>/edit',
         views.edit_response, name="edit_response"),
    path('stakeholders/form/<str:code>/responses/delete',
         views.delete_responses, name="delete_responses"),
    path('stakeholders/sendformlink', views.send_form_link, name="send-form-link")

]