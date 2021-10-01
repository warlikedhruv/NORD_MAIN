from organisations.models import Tenant
from django.db import models
from django.utils.timezone import now
from languages.models import Language
from users.models import User
import datetime
# Create your models here.

class Question(models.Model):

    #Question Fields
    question = models.TextField(null=True, blank=False) 
    description = models.TextField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    # language = models.ForeignKey(Language, related_name='lang_ques' ,on_delete=models.CASCADE, null=True)
    language = models.CharField(max_length=10, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)
    set_goal = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return str(self.question)

class Answer(models.Model):
    #Answer Fields
    attempted = 'OK'
    not_attempted = 'NA'
    status_choice = [
        (attempted, 'attempted'),
        (not_attempted, 'not attempted'),
    ]
    question = models.ForeignKey(Question,related_name='answer_ques', on_delete=models.CASCADE, null=True,blank=True)
    organisation = models.ForeignKey(Tenant,related_name='answer_org', on_delete=models.CASCADE, null=True,blank=True)
    user = models.ForeignKey(User,related_name='answer_user', on_delete=models.CASCADE, null=True,blank=True)
    value = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=2,choices=status_choice,default=not_attempted)
    comment = models.TextField(null=True, blank=True)
    optional = models.BooleanField(default=False)
    year = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(default=now)
    set_goal = models.BooleanField(blank=True, default=False)
    goal_answer = models.TextField(null=True, blank=True)
    goal_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return '--- Answer ID {} --- Question {}'.format(self.id, self.question)

class Category(models.Model):

    type_choice = [

        ('framework','framework'),
        ('category','category'),
        ('sub_category', 'sub_category')

    ]


    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=12 ,choices=type_choice, default = 'category')
    language = models.CharField(max_length=10, null=True, blank=True)
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.name)



class CategoryMapping(models.Model):

    framework = models.ForeignKey(Category, related_name='framework_category' , on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='category_category' , on_delete=models.CASCADE) 
    sub_category = models.ForeignKey(Category, related_name='subcategory_category' , on_delete=models.CASCADE) 
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)

    def __str__(self):
        return '{} -> {} -> {}'.format(self.framework.name,self.category.name,self.sub_category.name)


class QuestionCategoryMapping(models.Model):

    ques_map =  models.ForeignKey(Question, related_name='mapped_ques' , on_delete=models.CASCADE)
    cate = models.ForeignKey(CategoryMapping, related_name='sub_cate' , on_delete=models.CASCADE) 
    created_on = models.DateTimeField(default=now)
    updated_on = models.DateTimeField(default=now)

    def __str__(self):
        return '{} -> {}'.format(self.cate.sub_category.name,self.ques_map.question)

