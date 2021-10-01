from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

# Register your models here.
from .models import *

class QuestionAdmin(admin.ModelAdmin):
    search_fields=('question',)
    # list_display=[]
    # list_filter=[]

class CategoryAdmin(admin.ModelAdmin):
    search_fields=('name',)
    list_display=['name','type','language']
    list_filter=['type']

class CategoryMappingAdmin(admin.ModelAdmin):
    list_filter=['framework']

class QuestionCategoryMappingAdmin(admin.ModelAdmin):
    list_filter=['cate']

class AnswerAdmin(admin.ModelAdmin):
    list_filter=['organisation','year']

admin.site.register(Category,CategoryAdmin)
admin.site.register(CategoryMapping,CategoryMappingAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(QuestionCategoryMapping,QuestionCategoryMappingAdmin)
admin.site.register(Answer,AnswerAdmin)