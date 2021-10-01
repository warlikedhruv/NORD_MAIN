from django.urls import reverse
from users.permissions import check_viewing_rights_admin
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import (login_required,user_passes_test)
from django.shortcuts import render, redirect,get_object_or_404
from users.forms import DivErrorList
from django.utils.translation import gettext as _
# Create your views here.
@user_passes_test(check_viewing_rights_admin)
def create_organization(request):
    if request.method == 'POST':
        try:
            org_form = CreateOrganizationForm(request.POST,request.FILES)
            if org_form.is_valid():
                org_form.save()
                messages.success(request, f'New organization record created successfully!')
                return redirect('organization')
        except Exception as e:
            messages.error(request, f'Something happened in there. Please try again.')
            return redirect('create-org')
    else:
        org_form = CreateOrganizationForm()
    return render(request, 'organisation/create_org.html', {'org_form': org_form})


@user_passes_test(check_viewing_rights_admin)
def delete_organization(request,id):
    try:
        print('give id ',id)
        org = Tenant.objects.get(id=id)
        print('Deleting..',org.organisation_name)
        org.delete()
        messages.success(request, _("Record deleted successfully."))
        return redirect('organization')
    except Exception as e:
        messages.error(request, _("Some error occurred!. Please try again."))
        return redirect(reverse('organization'))


@user_passes_test(check_viewing_rights_admin)
def update_organization(request,id):
    try:
        org = Tenant.objects.get(id=id)
        #print('Got Updated Org ID')
        if request.method == 'POST':
            #print('In post Method..')
            org_form = OrganizationUpadateForm(request.POST, instance=org, error_class=DivErrorList)
            #print('Taken Form..')
            if org_form.is_valid():
                #print('form valid')
                org_form.save()
                messages.success(request, _("Record has been updated successfully!"))
                return redirect(reverse('organization'))
        else:
            #print('creating form..')
            org_form = OrganizationUpadateForm(instance=org)
        data = {'org_form': org_form, "org_id": id}
        return render(request, 'organisation/edit_org.html', data)
    except Exception as e:
        print(e)
        messages.error(request, _("No record found!"))
        return redirect(reverse('organization'))

