from django.http import Http404
from django.shortcuts import render, redirect,get_object_or_404
from MainApp.models import Snippet


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