from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from MainApp import views
from django.contrib import admin

urlpatterns = [
    # path('', include('MainApp.urls')),
    path('', views.index_page, name='home'),
    path('snippets/add', views.add_snippet_page, name='snippet-add'),
    path('snippets/list', views.snippets_page, {'snippets_my': False}, name='snippets-list'),
    path('snippets/my', views.snippets_page, {'snippets_my': True}, name='snippets-my'),
    path('snippet/<int:id>', views.snippet_detail, name='snippet-id'),
    path('snippet/<int:id>/delete', views.snippet_delete, name='snippet-delete'),
    path('snippet/<int:id>/edit', views.snippet_edit, name='snippet-edit'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('registration/', views.user_registration, name='registration'),
    path('comment/add', views.comment_add, name="comment_add"),
    path('stats/', views.stats_snippets, name="stats_snippets"),
    path('notifications/', views.user_notifications, name="notifications"),
    path('notifications/<int:id>/delete', views.notification_delete, name="notification-delete"),
    path('admin/', admin.site.urls),
    path('api/notifications/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),
    # path('api/comment/<int:id>/<str:str>', views.like_dislike, name='like_dislike'),
    path('api/comment/vote/', views.comment_like_dislike, name='comment_like_dislike'),

]
# snippets/list
# snippets/list?sort=name
# snippets/list?sort=lang
# snippets/list?sort=create_date

# api/comment/3/like
# api/comment/3/dislike
