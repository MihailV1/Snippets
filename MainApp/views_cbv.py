from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView, FormView
from django.contrib import messages, auth
from django_extensions import logging

from MainApp.forms import SnippetForm, CommentForm, UserRegistrationForm
from MainApp.models import Snippet, Comment, Notification, LANG_CHOICES
from MainApp.utils import send_activation_email
import logging

class AddSnippetView(LoginRequiredMixin, CreateView):
    """Создание нового сниппета"""
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/add_snippet.html'
    success_url = reverse_lazy('snippets-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Создание сниппета'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Success!!!")
        return super().form_valid(form)


class SnippetDetailView(DetailView):
    model = Snippet
    template_name = 'pages/snippet_detail.html'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        snippet = Snippet.objects.prefetch_related(
            Prefetch('comments',
                     queryset=Comment.with_likes_count().select_related('author')),
            "tags")
        return snippet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_form = CommentForm()
        snippet = self.get_object()
        context['pagename'] = f'Сниппет: {snippet.name}'
        context["comments_form"] = comments_form
        return context


class UserLogoutView(View):

    def get(self, request):
        auth.logout(request)
        return redirect('home')
    # POST -> GET
    # GET - ничего не меняется в проекте в базе данных,
    # POST - изменение в BD


# CBV
# 1. Уменьшается дублирование кода
# 2.
class UserNotificationsView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'pages/notifications.html'
    context_object_name = "notifications"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Мои уведомления'
        return context

    def get_queryset(self):
        notifications = Notification.objects.filter(recipient=self.request.user)
        # Отмечаем все уведомления как прочитанные при переходе на страницу
        Notification.objects.filter(recipient=self.request.user).update(is_read=True)
        return notifications


class SnippetsListView(ListView):
    """Отображение списка сниппетов с фильтрацией, поиском и сортировкой"""
    model = Snippet
    template_name = 'pages/view_snippets.html'
    context_object_name = 'snippets'
    paginate_by = 5

    def get_queryset(self):
        my_snippets = self.kwargs.get('snippets_my', False)

        if my_snippets:
            if not self.request.user.is_authenticated:
                raise PermissionDenied
            queryset = Snippet.objects.filter(user=self.request.user)
        else:
            if self.request.user.is_authenticated:  # auth: all public + self private
                queryset = Snippet.objects.filter(
                    # Q(public=True) | Q(public=False, user=self.request.user),
                    Q(public=True) | Q(user=self.request.user)

                ).select_related("user")
            else:  # not auth: all public
                queryset = Snippet.objects.filter(public=True).select_related("user")

        # Поиск
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )

        # Фильтрация по языку
        lang = self.request.GET.get("lang")
        if lang:
            queryset = queryset.filter(lang=lang)

        # Фильтрация по пользователю
        user_id = self.request.GET.get("user_id")
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        # Сортировка
        sort = self.request.GET.get("sort")
        if sort:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        my_snippets = self.kwargs.get('snippets_my', False)

        if my_snippets:
            context['pagename'] = 'Мои сниппеты'
        else:
            context['pagename'] = 'Просмотр сниппетов'

        # Получаем пользователей со сниппетами
        users = User.objects.filter(snippet__isnull=False).distinct()

        context.update({
            'sort': self.request.GET.get("sort"),
            'LANG_CHOICES': LANG_CHOICES,
            'users': users,
            'lang': self.request.GET.get("lang"),
            'user_id': self.request.GET.get("user_id")
        })

        return context


class SnippetEditView(LoginRequiredMixin, UpdateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/add_snippet.html'
    success_url = reverse_lazy('snippets-list')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pagename"] = 'Редактирование сниппета'
        context["edit"] = True
        context["id"] = self.kwargs.get("id")
        return context

logger = logging.getLogger(__name__)
class UserRegistrationView(FormView):
    template_name = 'pages/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')  # безопасный redirect на главную

    def form_valid(self, form):
        """
        Вызывается, если форма прошла валидацию (form.is_valid() == True)
        """
        try:
            # Сохраняем пользователя через форму
            user = form.save()  # 🚩 user уже is_active=False внутри формы
            logger.info("Пользователь '%s' успешно зарегистрирован (id=%d)", user.username, user.id)

            # Отправляем письмо с активацией
            send_activation_email(user, self.request)

            # Показываем пользователю уведомление
            messages.success(self.request, f"Пользователь {user.username} успешно зарегистрирован! "
                                           f"Пожалуйста, подтвердите email для активации аккаунта.")

            return super().form_valid(form)

        except Exception as e:
            logger.exception("Ошибка при регистрации пользователя: %s", str(e))
            messages.error(self.request, "Произошла непредвиденная ошибка! Попробуйте ещё раз.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Вызывается, если форма не прошла валидацию.
        Автоматически передаёт ошибки обратно в шаблон.
        """
        logger.warning("Ошибка регистрации. Ошибки формы: %s", form.errors.as_json())
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Добавляем в контекст переменные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['user_form'] = context['form']  # добавляем user_form для шаблона
        context['pagename'] = 'Регистрация'
        return context