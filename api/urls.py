from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('reader/', views.reader_dashboard, name='reader-dashboard'),
    path('journalist/', views.journalist_dashboard, name='journalist-dashboard'),
    path('editor/', views.editor_dashboard, name='editor-dashboard'),
    path('publisher/', views.publisher_dashboard, name='publisher-dashboard'),

    path('articles/', views.article_list, name='article-list'),
    path('articles/create/', views.create_article, name='article-create'),  
    path('articles/<int:pk>/', views.article_detail, name='article-detail'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article-edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article-delete'),

    path('approve/', views.approval_queue, name='approve'),

    path('approve/<int:article_id>/', views.approve_article, name='approve_article'),

    path('approvals/', views.approval_queue, name='approval-queue'),
    path('approvals/<int:pk>/approve/', views.approve_article, name='approve-article'),

    path('newsletters/', views.newsletter_list, name='newsletter-list'),
    path('newsletters/create/', views.newsletter_create, name='newsletter-create'),
    path('newsletters/<int:pk>/', views.newsletter_detail, name='newsletter-detail'),
    path('newsletters/<int:pk>/edit/', views.newsletter_edit, name='newsletter-edit'),
    path('newsletters/<int:pk>/delete/', views.newsletter_delete, name='newsletter-delete'),

    path('subscriptions/', views.manage_subscriptions, name='manage-subscriptions'),

    path('api/', include('api.api_urls')),
    path('api/articles/<int:pk>/approve/', views.approve_article),
]