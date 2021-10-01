import django_filters
from django_filters import CharFilter
from organisations.models import *
from questions.models import *
from users.models import *

class OrganisationFilter(django_filters.FilterSet):
    organisation_name = CharFilter(field_name='organisation_name', lookup_expr='icontains')
    class Meta:
        model = Tenant
        fields = ['organisation_name']


# class QestionFilter(django_filters.FilterSet):
#     class Meta:
#         model = QuestionCategoryMapping
#         fields = ['cate']


class UserFilter(django_filters.FilterSet):
    email = CharFilter(field_name='email', lookup_expr='icontains')
    f_name = CharFilter(field_name='f_name', lookup_expr='icontains')
    class Meta:
        model = User
        fields = ['email','f_name']

class QuestionsFilter(django_filters.FilterSet):
    class Meta:
        model = CategoryMapping
        fields = ['framework','category','sub_category']
    

# #To Get All FrameWork Names
#
# #To Get All Categorcates_mapping.objects.select_related('framework').filter(framework_type='framework').values('framework_name').distinct()y Names
# cates_mapping.objects.select_related('category').filter(category_type='category').values('category_name').distinct()
# # To get Questions Based on FrameWork id
# ques_cat_mapping.objects.select_related('cate').filter(cate__framework=10) #framework_id = 10
# # To get Questions Based on Category id
# ques_cat_mapping.objects.select_related('cate').filter(cate__category=11) #Category_id = 11