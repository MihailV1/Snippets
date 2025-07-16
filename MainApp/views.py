from django.core.exceptions import PermissionDenied
from django.http import Http404 , HttpResponse#, Http403
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth # Импортируем модуль auth
from django.db.models import F, Q, Count, Avg
from MainApp.models import Snippet, Comment, LANG_CHOICES
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from MainApp.models import LANG_ICON
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.contrib.auth.models import User

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
            public = form.cleaned_data['public']
            tags = form.cleaned_data['tags'] # QuerySet тегов
            # print("\n\n")
            # print(tags)
            snippet = Snippet.objects.create(name=name, lang=lang, code=code, description=description, user_id=request.user.id , public=public)
            snippet.tags.set(tags)  # или snippet.tags.add(*tags)
            # print("\n\n")
            return redirect('snippets-list')
        else:
            context = {'form': form, 'edit': False, 'pagename': 'Создание Сниппета'}
            return render(request, 'pages/add_snippet.html',
                          context)

# snippets/list?sort=name
# snippets/list?sort=lang
# snippets/list?sort=create_date
# snippets/list?page=2
def snippets_page(request, snippets_my):
    if snippets_my:  # url: snippets/my
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        snippets = Snippet.objects.filter(user=request.user)
        pagename = "Просмотр моих сниппетов"
    else:
        if not request.user.is_authenticated:  # not auth: all public snippets
            snippets = Snippet.objects.filter(public=True)
        else:  # auth:     all public snippets + OR self private snippets
            snippets = Snippet.objects.filter(Q(public=True) | Q(public=False, user=request.user))
        pagename = "Просмотр сниппетов"

    form = SnippetForm()

    # if not request.user.is_authenticated:
    #     snippets = Snippet.objects.filter(public=True)
    # else:
    #     snippets = Snippet.objects.filter(Q(public=True) | Q(public=False, user_id=request.user.id))
    sort = request.GET.get('sort')
    if sort is not None:
        # print(f"\n\n\n\nsort: {sort}\n\n\n\n")
        snippets = snippets.order_by(sort)
        # filter
    lang = request.GET.get("lang")
    if lang:
        snippets = snippets.filter(lang=lang)
    user_id = request.GET.get("user_id")
    if user_id:
        snippets = snippets.filter(user__id=user_id)

    snippet_count= len(snippets)
    # for snippet in snippets:
    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)

    # paginator
    paginator = Paginator(snippets, 10)  # Показывать по 10 сниппетов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Получаем объект Page для запрошенной страницы

    # Только пользователи, у которых есть хотя бы один сниппет
    active_users = User.objects.annotate(snippet_count=Count('snippet', filter=Q(snippet__public=True))).filter(snippet_count__gt=0)
    context = {'pagename': pagename,
               # 'snippets': snippets,
               # 'snippets': page_obj.object_list, # Это то же самое, что page_obj в цикле for в шаблоне
               'page_obj': page_obj,
               'snippet_count': snippet_count,
               'icon': get_icon(snippets),
                # 'public': snippet.public,
               'sort': sort,
               'LANG_CHOICES': LANG_CHOICES,
               # 'users': User.objects.all(),
               'users': active_users,
               'lang': lang,
               }
    return render(request, 'pages/view_snippets.html', context)

# @login_required
# def snippets_my(request):
#     snippets = Snippet.objects.filter(user_id=request.user.id)
#     snippet_count= len(snippets)
#     for snippet in snippets:
#         snippet.icon = get_icon(snippet.lang)
#     context = {'pagename': 'Мои сниппеты',
#                'snippets': snippets,
#                'snippet_count': snippet_count,
#                'icon': get_icon(snippets),
#                 'public': snippet.public,}
#     print(f"snippet.user-->{snippet.user}   snippet.public-->{snippet.public}")
#     return render(request, 'pages/view_snippets.html', context)

def snippet_detail(request, id):
    # snippet = get_object_or_404(Snippet, id=id)
    snippet = Snippet.objects.prefetch_related('comments').get(id=id) #.order_by('lang','-creation_date')
    snippet.views_count = F('views_count') + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()
    # comments = Comment.objects.filter(snippet_id=id)
    # comments = snippet.comment_set.all().order_by('-creation_date') # Получаем все комментарии для данного сниппета

    comments = snippet.comments.all()
    comments_count = len(comments)

    tags = snippet.tags.all()

    sort = request.GET.get('sort')
    if sort is not None:
        # print(f"\n\n\n\nsort: {sort}\n\n\n\n")
        comments = comments.order_by(sort)
    # print(f"------------\n\n\n\ncomments_count = {comments_count}\n\n\n\n-------------")
    comment_form = CommentForm() # Передаем пустую форму для добавления комментариев
    context = {'pagename': 'Просмотр сниппета',
                       'snippet': snippet,
                        'comments': comments,
                        'comment_form': comment_form,
                        'comments_count': comments_count,
                        'sort': sort, # sort comments!
                        'tags': tags,
                        }
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
            snippet.public = form.cleaned_data['public']
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

def user_registration(request):
    if request.method == "GET":
        user_form = UserRegistrationForm()
        context = {
            "user_form": user_form, 'pagename': 'Регистрация'
        }
        return render(request, "pages/registration.html", context)

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            return redirect("home")
        else:
            context = {'user_form': user_form, 'pagename': 'Регистрация'}
            return render(request, "pages/registration.html", context)


def comment_add(request):
   if request.method == "POST":
      comment_form = CommentForm(request.POST)
      snippet_id = request.POST.get('snippet_id') # Получаем ID сниппета из формы
      snippet = get_object_or_404(Snippet, id=snippet_id)
      # print(f"\n\n\n\n------------------------------>snippet_id = {snippet_id}\n\n\n\n")
      if comment_form.is_valid():
         comment = comment_form.save(commit=False)
         comment.author = request.user # Текущий авторизованный пользователь
         comment.snippet = snippet
         comment.save()

      return redirect('snippet-id', id=snippet_id) # Предполагаем, что у вас есть URL для деталей сниппета с параметром pk

   raise Http404

def stats_snippets(request):
    # Всего сниппетов: # Публичных сниппетов
    stats = Snippet.objects.aggregate(all_snippets=Count('id')
                                      , all_p_snippets = Count('id', filter=Q(public=True))
                                      , avg_p_snippets = Avg('views_count', filter=Q(public=True))
                                      )
    top5_views_snippets = Snippet.objects.filter(public=True).order_by('-views_count')[:5]
    top3_users  = User.objects.annotate(top3_users_snippets_count = Count('snippet', filter=Q(snippet__public=True)))\
                                .filter(top3_users_snippets_count__gt=0).order_by('-top3_users_snippets_count')[:3]
    context = {'pagename': 'Статистика по сниппетам',
                        # 'all_snippets': all_snippets,
                       'all_snippets': stats['all_snippets'],
                       'all_p_snippets': stats['all_p_snippets'],
                       'avg_p_snippets': stats['avg_p_snippets'],
                        'top5_views_snippets': top5_views_snippets,
                        'top3_users': top3_users,
               }
    return render(request, 'pages/stats.html', context)