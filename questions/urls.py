from django.urls import path
from . import views
urlpatterns = [
   
    path('create-question/', views.create_question, name="create-question"),
    path('delete-question/<int:pk>', views.delete_question, name="delete-question"),
    path('question/edit/<int:pk>', views.update_question, name="edit-question"),
    path('upload-question/', views.upload_questions, name="upload-question"),
    path('create-cates/', views.create_cates, name="create-cates"),

]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)