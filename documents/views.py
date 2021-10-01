from django.shortcuts import redirect, render
from .models import Document,PrivateAccess
from .forms import DocumentForm,DocumentAccessForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from organisations.models import Tenant
from django.db.models.query_utils import Q

@login_required(login_url="/user-login")
def help(request):
    public_documents = Document.objects.filter(Q(doc_type="public") | Q(owner = request.user.id)).order_by('-id')
    private_documents = PrivateAccess.objects.filter(access_tenant=request.user.tenant)
    print('##### private_documents #####')
    print(private_documents)
    #print(Document.objects.all().values())
    return render(request, 'help/help.html',{'public_documents': public_documents,'private_documents':private_documents})


@login_required(login_url="/user-login")
def upload_document(request):
    if request.method == 'POST':
        try:
            print('recieved form..')
            form = DocumentForm(request.POST,request.FILES)
            if form.is_valid():
                print('form valid')
                document_form = form.save(commit=False)
                document_form.owner = request.user
                document_form.save()
                messages.success(request, f'Document Uploaded successfully!')
            else:
                for field, errors in form.errors.items():
                    print(errors)
                    messages.error(request,errors)
                return redirect('upload-document')
            return redirect('view-docs')
        except Exception as e:
            messages.error(request, f'Document Upload Failed, Please try again.')
            return redirect('upload-document')
    else:
        doc_form = DocumentForm()
    return render(request, 'help/file_upload.html', {'doc_form': doc_form})

@login_required(login_url="/user-login")
def delete_document(request,id):
    try:
        doc = Document.objects.get(id=id)
        if request.user == doc.owner:
            print('You are the owner deleting the file..')
            doc.delete()
            messages.success(request, _("Document deleted successfully."))
            return redirect('view-docs')
        else:
            print('You are the not the owner cannot delete the file..')
            messages.error(request,_("Only Admin can delete the file."))
        return redirect('view-docs')
    except Exception as e:
        messages.error(request, _("Some error occurred!. Please try again."))
        return redirect(reverse('view-docs'))

@login_required(login_url="/user-login")
def change_doc_type(request,id):
    try:
        doc = Document.objects.get(id=id)
        if request.user == doc.owner:
            print('You are the owner so can change access of the file..')
            if doc.doc_type=="private":
                doc.doc_type="public"
            else:
                doc.doc_type="private"
            doc.save()
            messages.success(request, _("Access changed successfully."))
            return redirect('view-docs')
        else:
            print('Only Owner can change the access..')
            messages.error(request,_("Only Admin can change access the file."))
        return redirect(reverse('view-docs'))
    except Exception as e:
        messages.error(request, _("Some error occurred!. Please try again."))
        return redirect(reverse('view-docs'))

@login_required(login_url="/user-login")
def provide_access(request,id):
    if request.method == 'POST':
        try:
            doc = DocumentAccessForm(request.POST)
            if doc.is_valid():
                doc_access=PrivateAccess(doc = Document.objects.get(id = id),
                     access_tenant = Tenant.objects.get(organisation_name=doc.cleaned_data['tenant']))
                doc_access.save()
            messages.success(request, f'Access Granted successfully!')
            return redirect(reverse('view-docs'))
        except Exception as e:
            print(e)
            messages.error(request, f'Something happened in there. Please try again.')
            return redirect(reverse('view-docs'))
    else:
        doc_form = DocumentAccessForm()
        doc_name = Document.objects.values('document_name').get(id=id)['document_name']
        doc_access=PrivateAccess.objects.filter(doc = id)
    return render(request, 'help/provide_doc_access.html', {'doc_form': doc_form,'doc_access':doc_access,'doc_name':doc_name})


@login_required(login_url="/user-login")
def delete_access(request,id):
    try:
        if request.user.user_type=="admin":
            doc = PrivateAccess.objects.get(id=id)
            doc.delete()
            messages.success(request, _("Access Revoked successfully."))
            return redirect('view-docs')
        else:
            print('You are the not the owner cannot delete the Access..')
            messages.error(request,_("Only Admin can delete the Access."))
        return redirect(reverse('view-docs'))
    except Exception as e:
        messages.error(request, _("Some error occurred!. Please try again."))
        return redirect(reverse('view-docs'))