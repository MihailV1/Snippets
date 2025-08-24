from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse  # , Http403, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth  # Импортируем модуль auth
from django.db.models import F, Q, Count, Avg
from MainApp.models import Snippet, Comment, LANG_CHOICES, Notification, LikeDislike
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from MainApp.models import LANG_ICON, Tag
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from MainApp.signals import snippet_view
import logging

# Получаем экземпляр логгера
# Если вы настроили собственный логгер, используйте его имя, например:
logger = logging.getLogger(__name__)  # Рекомендуется использовать имя текущего модуля


def get_icon(lang):
    return LANG_ICON.get(lang)


# error -> danger
# debug -> dark

def index_page(request):
    context = {'pagename': 'PythonBin'}
    # messages.info(request, ' messages.info...')
    # messages.warning(request, 'messages.warning...')
    # messages.error(request, 'messages.error...')
    # messages.debug(request, 'messages.debug...')
    return render(request, 'pages/index.html', context)


@login_required
def add_snippet_page(request):
    if request.method == 'GET':
        form = SnippetForm()
        context = {'pagename': 'Создание Сниппета', 'edit': False, 'form': form}
        return render(request, 'pages/add_snippet.html', context)

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            # form.save()
            name = form.cleaned_data['name']
            lang = form.cleaned_data['lang']
            description = form.cleaned_data['description']
            code = form.cleaned_data['code']
            public = form.cleaned_data['public']
            tags = form.cleaned_data['tags']  # QuerySet тегов
            snippet = Snippet.objects.create(name=name, lang=lang, code=code, description=description,
                                             user_id=request.user.id, public=public)
            snippet.tags.set(tags)  # или snippet.tags.add(*tags)
            messages.info(request, f'Пользователь {snippet.user} успешно СОЗДАЛ сниппет (id={snippet.id})')
            return redirect('snippets-list')
        else:
            context = {'form': form, 'edit': False, 'pagename': 'Создание Сниппета'}
            messages.error(request, f"Форма заполнена не верно")
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

    # form = SnippetForm()
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

    # tags = request.GET.get("tags")    #  вернёт только одно (последнее) значение
    tags = request.GET.getlist("tags")  # все значения как список.
    if tags:
        # for tag in tags:
        #     # print(f"tag: {tag}")
        snippets = snippets.filter(
            tags__name__in=tags).distinct()  # distinct() нужен, чтобы избежать дубликатов, если сниппет совпал по нескольким тегам.
        # for snippet in snippets:
        #     print(f"snippet.tags.name: {snippet}")
    snippet_count = len(snippets)
    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
        if tags:
            snippet.tags_details = snippet.tags.filter(name__in=tags)
        else:
            snippet.tags_details = snippet.tags.all()

    # paginator
    paginator = Paginator(snippets, 10)  # Показывать по 10 сниппетов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Получаем объект Page для запрошенной страницы

    # Только пользователи, у которых есть хотя бы один сниппет
    active_users = User.objects.annotate(snippet_count=Count('snippet', filter=Q(snippet__public=True))).filter(
        snippet_count__gt=0)
    context = {'pagename': pagename,  # 'true' if snippets_my else 'false'
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
               'all_tags': Tag.objects.all(),
               'snippets_my': snippets_my,
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
    snippet = Snippet.objects.prefetch_related('comments').get(id=id)  # .order_by('lang','-creation_date')
    if snippet.user != request.user and snippet.public is False:
        return HttpResponseForbidden("You are not authorized to see this snippet")
    snippet_view.send(sender=None, snippet=snippet)
    # snippet.views_count = F('views_count') + 1
    # snippet.save(update_fields=['views_count'])
    # snippet.refresh_from_db()
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
    comment_form = CommentForm()  # Передаем пустую форму для добавления комментариев
    context = {'pagename': 'Просмотр сниппета',
               'pagename': f'Сниппет: {snippet.name}',
               'snippet': snippet,
               'comments': comments,
               'comment_form': comment_form,
               'comments_count': comments_count,
               'sort': sort,  # sort comments!
               'tags': tags,
               }
    return render(request, 'pages/snippet.html', context)


@login_required
def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        logger.warning("Пользователь '%s' НЕ ИМЕЕТ право удалить этот сниппет (id=%d)", snippet.user, snippet.id)
        context = {'pagename': 'Э! Какой умный!'}
        return render(request, 'pages/index.html', context)
    logger.info("Пользователь '%s' успешно удалил сниппет (id=%d)", snippet.user, snippet.id)
    messages.info(request, f'Пользователь {snippet.user} успешно удалил сниппет (id={snippet.id})')
    snippet.delete()
    return redirect('snippets-list')


@login_required
def snippet_edit(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if request.method == 'GET':
        form = SnippetForm(initial={
            'name': snippet.name,
            'public': snippet.public,
            'lang': snippet.lang,
            'code': snippet.code,
            'description': snippet.description,
            'tags': snippet.tags.all(),
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
            tags = form.cleaned_data['tags']  # QuerySet тегов
            snippet.tags.add(*tags)  # или snippet.tags.set(*tags)
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
                "errors": ["Некорректные данные"],
            }
            print(f"------------->user={user}")
            return render(request, "pages/index.html", context)
    context = {'pagename': 'Э! Какой умный!'}
    return render(request, 'pages/index.html', context)


def user_logout(request):
    auth.logout(request)
    return redirect('home')


def user_registration(request):
    try:
        if request.method == "GET":
            user_form = UserRegistrationForm()
            context = {
                "user_form": user_form,
                'pagename': 'Регистрация'
            }
            return render(request, "pages/registration.html", context)

        if request.method == "POST":
            post_data = request.POST.copy()
            # post_data.pop('csrfmiddlewaretoken', None)  # Удаляем ключ, если есть
            for key in ['csrfmiddlewaretoken', 'password1', 'password2']:
                post_data.pop(key, None)
            logger.debug("POST запрос на регистрацию пользователя. Данные: %s", post_data.dict())
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                user = user_form.save()
                logger.info("Пользователь '%s' успешно зарегистрирован (id=%d)", user.username, user.id)
                messages.success(request, f"User {user.username} pasted successfully!")
                return redirect("home")
            else:
                logger.warning("Ошибка регистрации. Ошибки формы: %s", user_form.errors.as_json())
                context = {'user_form': user_form, 'pagename': 'Регистрация'}
                return render(request, "pages/registration.html", context)
    except Exception as e:
        # Логируем исключение и стек вызовов
        logger.exception("Ошибка в функции user_registration: %s", str(e))
        messages.error(request, "Произошла непредвиденная ошибка! Попробуйте еще раз.")
        return redirect("home")


# def user_registration(request):
#     if request.method == "GET":
#         user_form = UserRegistrationForm()
#         context = {
#             "user_form": user_form, 'pagename': 'Регистрация'
#         }
#         return render(request, "pages/registration.html", context)
#
#     if request.method == "POST":
#         user_form = UserRegistrationForm(request.POST)
#         if user_form.is_valid():
#             user = user_form.save()
#             messages.success(request, f"User {user.username} pasted successfully!")
#             return redirect("home")
#         else:
#             context = {'user_form': user_form, 'pagename': 'Регистрация'}
#             return render(request, "pages/registration.html", context)

@login_required
def comment_add(request):
    if request.method == "POST":
        snippet_id = request.POST.get('snippet_id')  # Получаем ID сниппета из формы
        snippet = get_object_or_404(Snippet, id=snippet_id)
        if not request.user.is_authenticated:
            messages.error(request, "Вы должны войти в систему, чтобы оставить комментарий.")
            # return redirect('snippet-id', id=snippet_id)
            return redirect('registration')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user  # Текущий авторизованный пользователь
            comment.snippet = snippet
            comment.save()
            messages.info(request, f'Пользователь {snippet.user} успешно ОСТАВИЛ комментарий (id={snippet.name})')
        return redirect('snippet-id',
                        id=snippet_id)  # Предполагаем, что у вас есть URL для деталей сниппета с параметром pk

    raise Http404


def stats_snippets(request):
    # Всего сниппетов: # Публичных сниппетов
    stats = Snippet.objects.aggregate(all_snippets=Count('id')
                                      , all_p_snippets=Count('id', filter=Q(public=True))
                                      , avg_p_snippets=Avg('views_count', filter=Q(public=True))
                                      )
    top5_views_snippets = Snippet.objects.filter(public=True).order_by('-views_count')[:5]
    top3_users = User.objects.annotate(top3_users_snippets_count=Count('snippet', filter=Q(snippet__public=True))) \
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


@login_required
def user_notifications(request):
    """Страница с уведомлениями пользователя"""

    # Получаем все уведомления для авторизованного пользователя, сортируем по дате создания
    notifications = list(Notification.objects.filter(recipient=request.user))
    # сколько комментариев
    # count_comment = notifications.filter(is_read=0).count()
    # Отмечаем все уведомления как прочитанные при переходе на страницу
    Notification.objects.filter(recipient=request.user).update(is_read=True)

    context = {
        'pagename': 'Мои уведомления',
        'notifications': notifications,
    }

    return render(request, 'pages/notifications.html', context)


# 0
# --> api/notifications/unread-count?last_count=0
# 1
# <-- 1
# --> api/notifications/unread-count?last_count=1
# 1
# 2
# <-- 2
# --> api/notifications/unread-count?last_count=2
# <-- 3

@login_required
def unread_notifications_count(request):
    """
    API endpoint для получения количества непрочитанных уведомлений
    Использует long polling - отвечает только если есть непрочитанные уведомления
    """
    import time

    # Максимальное время ожидания (30 секунд)
    max_wait_time = 30
    check_interval = 1  # Проверяем каждую секунду

    # last_count = int(request.GET.get("lastCount"))
    last_count = int(request.GET.get("last_count", 0))
    # print(f"last_count: {request.GET.get("last_count")}")
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        # Получаем количество непрочитанных уведомлений
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        # Если есть непрочитанные уведомления, сразу отвечаем
        if unread_count > last_count:
            return JsonResponse({
                'success': True,
                'unread_count': unread_count,
                'timestamp': str(datetime.now())
            })

        # Ждем перед следующей проверкой
        time.sleep(check_interval)

    # Если время истекло и нет уведомлений, возвращаем 0
    return JsonResponse({
        'success': True,
        'unread_count': 0,
        'timestamp': str(datetime.now())
    })


@login_required
def notification_delete(request, id):
    notification = get_object_or_404(Notification, id=id)
    # notif = Notification.objects.filter(recipient=request.id)
    # if snippet.user != request.user:
    #     logger.warning("Пользователь '%s' НЕ ИМЕЕТ право удалить этот сниппет (id=%d)", snippet.user, snippet.id)
    #     context = {'pagename': 'Э! Какой умный!'}
    #     return render(request, 'pages/index.html', context)
    # logger.info("уведомления '%s' успешно удалил request.user (id=%d)", snippet.user, request.user)
    # messages.info(request, f'Пользователь {snippet.user} успешно удалил сниппет (id={snippet.id})')
    notification.delete()
    return redirect('notifications')


@login_required
def comment_like_dislike(request):
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            comment_id = data.get("comment_id")
            vote = data.get("vote")

            comment = Comment.objects.get(id=comment_id)

            # Проверяем, голосовал ли пользователь
            existing_vote, created = LikeDislike.objects.get_or_create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id,
                defaults={'vote': vote}
            )
            if not created:
                # Если уже голосовал, обновляем голос
                if existing_vote.vote != vote:
                    existing_vote.vote = vote
                    existing_vote.save()
                else:
                    # Если нажал повторно тот же голос → можно удалить
                    existing_vote.delete()
            return JsonResponse({"success": True,
                                 "likes": comment.likes_count,
                                 "dislikes": comment.dislikes_count})
        except Comment.DoesNotExist:
            return JsonResponse({"success": False, "message": "Комментарий не найден"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Метод не разрешен"})

@login_required
def snippet_like_dislike(request):
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            snippet_id = data.get("snippet_id")
            vote = data.get("vote")

            snippet = Snippet.objects.get(id=snippet_id)

            # Проверяем, голосовал ли пользователь
            existing_vote, created = LikeDislike.objects.get_or_create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Snippet),
                object_id=snippet.id,
                defaults={'vote': vote}
            )
            if not created:
                # Если уже голосовал, обновляем голос
                if existing_vote.vote != vote:
                    existing_vote.vote = vote
                    existing_vote.save()
                else:
                    # Если нажал повторно тот же голос → можно удалить
                    existing_vote.delete()
            return JsonResponse({"success": True,
                                 "likes": snippet.likes_count,
                                 "dislikes": snippet.dislikes_count})
        except Comment.DoesNotExist:
            return JsonResponse({"success": False, "message": "Комментарий не найден"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Метод не разрешен"})