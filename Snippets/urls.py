import debug_toolbar
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from MainApp import views, views_cbv
from django.contrib import admin

# from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
                  # path('', include('MainApp.urls')),
                  path('', views.index_page, name='home'),
                  path('snippets/add', views.add_snippet_page, name='snippet-add'),
                  # path('snippets/add', views_cbv.AddSnippetView.as_view(), name="snippet-add"),
                  # path('snippets/list', views.snippets_page, {'snippets_my': False}, name='snippets-list'),
                  path('snippets/list', views_cbv.SnippetsListView.as_view(), {'snippets_my': False},
                       name='snippets-list'),
                  # path('snippets/my', views.snippets_page, {'snippets_my': True}, name='snippets-my'),
                  path('snippets/my', views_cbv.SnippetsListView.as_view(), {'snippets_my': True}, name='snippets-my'),
                  path('snippet/<int:id>', views.snippet_detail, name='snippet-id'),
                  # path('snippet/<int:id>', views_cbv.SnippetDetailView.as_view(), name="snippet-detail"),
                  path('snippet/<int:id>/delete', views.snippet_delete, name='snippet-delete'),
                  path('snippet/<int:id>/edit', views_cbv.SnippetEditView.as_view(), name='snippet-edit'),
                  # path('snippet/<int:id>/edit', views.snippet_edit, name='snippet-edit'),
                  path('login/', views.login_page, name='login'),
                  # path('logout/', views.user_logout, name='logout'),
                  path('logout/', views_cbv.UserLogoutView.as_view(), name='logout'),
                  # path('registration/', views.user_registration, name='registration'),
                  path('registration/', views_cbv.UserRegistrationView.as_view(), name='registration'),
                  path('comment/add', views.comment_add, name="comment_add"),
                  path('stats/', views.stats_snippets, name="stats_snippets"),
                  # path('notifications/', views.user_notifications, name="notifications"),
                  path('notifications/', views_cbv.UserNotificationsView.as_view(), name="notifications"),
                  path('notifications/<int:id>/delete', views.notification_delete, name="notification-delete"),
                  path('admin/', admin.site.urls),
                  path('api/notifications/unread-count/', views.unread_notifications_count,
                       name='unread_notifications_count'),
                  path('activate/<int:user_id>/<str:token>/', views.activate_account, name="activate-account"),
                  # path('api/comment/<int:id>/<str:str>', views.like_dislike, name='like_dislike'),
                  path('api/comment/vote/', views.comment_like_dislike, name='comment_like_dislike'),
                  path('api/snippet/vote/', views.snippet_like_dislike, name='snippet_like_dislike'),
                  path('snippet/<int:id>/subscribe/', views.subscribe_to_snippet, name='subscribe-to-snippet'),
                  path('profile/', views.user_profile, name="user_profile"),
                  path('profile/edit', views.edit_profile, name="user_profile_edit"),
                  path('profile/edit', views.edit_profile, name="user_profile_edit"),
              ] #+ debug_toolbar_urls()

if settings.DEBUG:
    # Добавляем debug_toolbar URLs только в режиме разработки
    if settings.DEBUG:
        try:
            from debug_toolbar.toolbar import debug_toolbar_urls

            urlpatterns += [
                path('__debug__/', include(debug_toolbar.urls)),
            ]
        except ImportError:
            pass
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# snippets/list
# snippets/list?sort=name
# snippets/list?sort=lang
# snippets/list?sort=create_date

# api/comment/3/like
# api/comment/3/dislike
