from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import DocumentForm

from .file_processor import handle_uploaded_file
from .processor_simple_ms1 import simple_ms1_processor
from .processor_dia import dia_processor
from .process_topn import topn_processor
from .processor_varytopn import varying_topn_processor
# Create your views here.


def home(request):
    return render(request, 'vimss_app/home.html')


def simple_ms1(request):
    if request.method == 'POST':
        # print(request.FILES.getlist("document"),'#'*10)
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

            handle_uploaded_file(request.FILES['document'], 'simple_ms1')

            result_path = simple_ms1_processor()
            processed_files = [result_path]
            form.save()
            # return redirect('home')
            return render(request, 'vimss_app/simple_ms1.html', {
                        'form': form, 'processed_files': processed_files
                    })
    else:
        form = DocumentForm()
    return render(request, 'vimss_app/simple_ms1.html', {
        'form': form
    })



def dia(request):
    processed_files = []
    if(request.GET.get('dia_btn')):
        # print( int(request.GET.get('mytextbox')) )
        result_path = dia_processor()
        processed_files = [result_path]
    return render(request, 'vimss_app/dia.html',{'processed_files': processed_files})


def top_n(request):
    processed_files = []
    if(request.GET.get('topn_btn')):
        # print( int(request.GET.get('mytextbox')) )
        path_list = topn_processor()
        processed_files = path_list
    elif (request.GET.get('varyingtopn_btn')):
        path_list = varying_topn_processor()
        processed_files = path_list
    return render(request, 'vimss_app/top_n.html',{'processed_files': processed_files})


def multiple_sample(request):
    return render(request, 'vimss_app/multiple_sample.html')