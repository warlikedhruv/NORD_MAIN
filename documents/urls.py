from users import views
from django.urls import path
from .views import *
urlpatterns = [
    path("upload_document/",upload_document,name='upload-document'),
    path('delete_document/<int:id>/',delete_document,name="delete-document"),
    path('change_doc_type/<int:id>/',change_doc_type,name='change-doc-type'),
    path('provide_access/<int:id>/',provide_access,name='provide-access'),
    path('delete_access/<int:id>/',delete_access,name='delete-access'),
    path('user-document/', help, name="view-docs"),
]