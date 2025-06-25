from django.http import Http404
from django.shortcuts import render, redirect,get_object_or_404
from MainApp.models import Snippet
from MainApp.forms import SnippetForm



def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    context = {'pagename': 'Добавление нового сниппета'}
    return render(request, 'pages/add_snippet.html', context)


def snippets_page(request):
    snippets = Snippet.objects.all()
    snippet_count= len(snippets)
    context = {'pagename': 'Просмотр сниппетов',
               'snippets': snippets,
               'snippet_count': snippet_count}
    return render(request, 'pages/view_snippets.html', context)

def snippet_detail(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    context = {'pagename': 'Просмотр сниппета',
                       'snippet': snippet,}
    return render(request, 'pages/snippet.html', context)

    # try:
    #     snippets = Snippet.objects.get(id=id)
    #     context = {'pagename': 'Просмотр сниппета',
    #                    'snippets': snippets,}
    #     return render(request, 'pages/snippet.html', context)
    # except Snippet.DoesNotExist:
    #     raise Http404

def snippet_create(request):
    if request.method == 'GET':
        form = SnippetForm()
        # print(f"FORM METHOD -> {request.method}")
        return render(request, 'pages/add_snippet.html', {'form': form})

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        # print(f"FORM DATA: {request.POST}")
        if form.is_valid():
            name = form.cleaned_data['name']
            lang = form.cleaned_data['lang']
            code = form.cleaned_data['code']

            Snippet.objects.create(name=name, lang=lang, code=code)
            return redirect('snippets-list')
        else:
            return render(request, 'pages/add_snippet.html', {'form': form})