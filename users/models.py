from nord_esg.settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from organisations.models import Tenant
from django.utils import timezone
from languages.models import Language
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, tenant, f_name = None, password=None, l_name = None):
        if self.model.objects.filter(email=email).exists():
            raise ValueError("Already Exist")
        user = self.model(email = self.normalize_email(email),
                            f_name = f_name,
                            l_name = l_name,
                            tenant = tenant
                            )
        user.set_password(password)
        user.save(using=self._db)
        
        return user


    def create_superuser(self, email, password=None ):
        # create database super_use/r         
        if self.model.objects.filter(email=email).exists():
            raise ValueError("Already Exist")
        user = self.model(email = self.normalize_email(email))
        user.set_password(password)

        user.is_staff = True
        user.is_superuser = True
        user.user_type = 'admin'
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
        
    # Custom user model for user authentication 

    user_type_choice = [

        ('admin','admin'),
        ('user','user'),

    ]
    email = models.EmailField(max_length=255, unique=True)
    f_name = models.CharField(max_length=255,null=True, blank=False)
    l_name = models.CharField(max_length=255, default="", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    tenant = models.ForeignKey(Tenant, related_name='tenant_1' ,on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey(Language, related_name='user_lang' ,on_delete=models.CASCADE,null=True, blank=False)
    f_login = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(default=timezone.now)
    user_type = models.CharField(max_length=11 ,choices=user_type_choice, default = 'user')
    image = models.ImageField("image", null=True, blank=True, upload_to='profile_pics')
    country = models.CharField(max_length=255,null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        ordering = ['created_on', 'tenant']    


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []




# class email_link_expire(models.Model):

    # user_id = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    # expire_by = models.DateTimeField()
    # count = models.IntegerField(default=0)
    # date_time = models.DateTimeField(default=now)






