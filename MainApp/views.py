from django.http import Http404
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth # Импортируем модуль auth
from django.db.models import F
from MainApp.models import Snippet
from MainApp.forms import SnippetForm
from MainApp.models import LANG_ICON
from django.contrib.auth.decorators import login_required

def get_icon(lang):
    return LANG_ICON.get(lang)


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)

@login_required
def add_snippet_page(request):
    if request.method == 'GET':
        form = SnippetForm()
        # print(f"FORM METHOD -> {request.method}")
        context = {'pagename': 'Создание Сниппета', 'edit': False, 'form': form}
        return render(request, 'pages/add_snippet.html', context)

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        # print(f"FORM DATA: {request.POST}")
        if form.is_valid():
            # form.save()
            name = form.cleaned_data['name']
            lang = form.cleaned_data['lang']
            description = form.cleaned_data['description']
            code = form.cleaned_data['code']
            Snippet.objects.create(name=name, lang=lang, code=code, description=description, user_id=request.user.id)
            return redirect('snippets-list')
        else:
            context = {'form': form, 'edit': False, 'pagename': 'Создание Сниппета'}
            return render(request, 'pages/add_snippet.html',
                          context)


def snippets_page(request):
    snippets = Snippet.objects.all()
    snippet_count= len(snippets)
    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
    context = {'pagename': 'Просмотр сниппетов',
               'snippets': snippets,
               'snippet_count': snippet_count,
               'icon': get_icon(snippets)}
    return render(request, 'pages/view_snippets.html', context)

def snippets_my(request):
    snippets = Snippet.objects.filter(user_id=request.user.id)
    snippet_count= len(snippets)
    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
    context = {'pagename': 'Мои сниппеты',
               'snippets': snippets,
               'snippet_count': snippet_count,
               'icon': get_icon(snippets)}
    return render(request, 'pages/view_snippets.html', context)

def snippet_detail(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    snippet.views_count = F('views_count') + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()
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

# def snippet_create(request):
#     if request.method == 'GET':
#         form = SnippetForm()
#         print(f"FORM METHOD -> {request.method}")
#         return render(request, 'pages/add_snippet.html', {'form': form})
#
#     if request.method == 'POST':
#         form = SnippetForm(request.POST)
#         print(f"FORM DATA: {request.POST}")
#         print(f"request.method == 'POST' FORM: {form}")
#         if form.is_valid():
#             # form.save()
#             name = form.cleaned_data['name']
#             lang = form.cleaned_data['lang']
#             description = form.cleaned_data['description']
#             code = form.cleaned_data['code']
#             Snippet.objects.create(name=name, lang=lang, code=code, description=description)
#
#             return redirect('snippets-list')
#         else:
#             return render(request, 'pages/add_snippet.html',
#                           {'form': form, 'pagename': "Создание Сниппет"})

@login_required
def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        context = {'pagename': 'Э! Какой умный!'}
        return render(request, 'pages/index.html', context)
    snippet.delete()
    return redirect('snippets-list')

@login_required
def snippet_edit(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if request.method == 'GET':
        form =SnippetForm(initial={
            'name': snippet.name,
            'lang': snippet.lang,
            'code': snippet.code,
            'description': snippet.description,
        })
        # print(f"StartFORM ->\n{form}\nendFORM")
    # context = {'form': form, 'edit': True,'id': id}
        context = {
            'form': form,
            'pagename': 'Редактирование сниппета',
            'edit': True,
            'id': snippet.id
        }
        return render(request, 'pages/add_snippet.html', context)
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if snippet.user != request.user:
            context = {'pagename': 'Э! Какой умный!'}
            return render(request, 'pages/index.html', context)
        if form.is_valid():
            snippet.name = form.cleaned_data['name']
            snippet.lang = form.cleaned_data['lang']
            snippet.code = form.cleaned_data['code']
            snippet.description = form.cleaned_data['description']
            snippet.save()
            return redirect('snippets-list')
        else:
            # ❗ Обработка случая, когда форма НЕ прошла валидацию
            context = {
                'form': form,
                'pagename': 'Редактирование сниппета',
                'edit': True,
                'id': snippet.id
            }
            return render(request, 'pages/add_snippet.html', context)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Попытка аутентификации пользователя
        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            # Если пользователь аутентифицирован, выполняем вход
            auth.login(request, user)
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
            # # Перенаправляем пользователя на домашнюю страницу:
            # print(f"------------->user={user}")
            # return redirect('home') # 'home' - это имя вашего URL для домашней страницы
        else:
            # Если аутентификация не удалась, можно вывести сообщение об ошибке
            context = {
                "errors" : ["Некорректные данные"],
            }
            print(f"------------->user={user}")
            return render(request, "pages/index.html", context)
    context = {'pagename': 'Э! Какой умный!'}
    return render(request,'pages/index.html', context)

def user_logout(request):
    auth.logout(request)
    return redirect('home')
