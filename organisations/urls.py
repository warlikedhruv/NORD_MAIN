from django.urls import path
from . import views
urlpatterns = [
    path('create-org/', views.create_organization, name="create-org"),
    path('delete-org/<int:id>/', views.delete_organization, name="delete-org"),
    path('edit-org/<int:id>/', views.update_organization, name="edit-org"),
]
