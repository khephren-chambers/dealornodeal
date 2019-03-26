from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import Document
from .forms import DocumentForm
from django.template import loader


def save_uploaded_file(request):
    '''
    Saves an uploaded PDF file.
    '''
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = Document(docfile = request.FILES['docfile'])
            document.save()

            # Redirect after submitting document.
            return HttpResponseRedirect('/thanks')
    else:
        form = DocumentForm() # A empty, unbound form
        #return HttpResponse('Thank you!')
    return render(request, 'uploader/uploadertemp.html', {'form': form})


def thank_you(request):
    '''
    Directs a user to the thank you page.
    '''

    return render(request, 'uploader/thanks.html')