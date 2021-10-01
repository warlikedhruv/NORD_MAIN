from django.db import models
import os
import random
from django.utils.timezone import now
from organisations.models import Tenant
from users.models import User
from .validators import validate_file_size
# Create your models here.


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_file_path(instance, filename):
    print(instance)
    print(filename)
    new_filename = random.randint(1,999999999)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    print("Hello Upload")
    return "docs/{new_filename}/{final_filename}".format(
                new_filename=new_filename,
                final_filename=final_filename
                )




class Document(models.Model):

    file_type = [
        ('public', 'public'),
        ('private', 'private')
    ]

    document_name = models.CharField(max_length=100)
    document_description = models.TextField()
    document = models.FileField(upload_to=upload_file_path,validators=[validate_file_size])
    doc_type = models.CharField(max_length=7, choices=file_type, null = True, blank=False)
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)
    owner = models.ForeignKey(User,related_name='docs', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.document_name)

class PrivateAccess(models.Model):

    doc = models.ForeignKey(Document, related_name='docu' , on_delete=models.CASCADE, null=True, blank=True)
    access_tenant = models.ForeignKey(Tenant, related_name='ten', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)

    def __str__(self):
        return '{} shared to {}'.format(self.doc.document_name,self.access_tenant.organisation_name)