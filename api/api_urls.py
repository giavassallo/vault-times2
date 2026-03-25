from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api_views import (
    ArticleListCreateAPIView,
    ArticleSubscribedAPIView,
    ArticleRetrieveUpdateDestroyAPIView,
    ApprovedWebhookAPIView,
    NewsletterListCreateAPIView,
    NewsletterRetrieveUpdateDestroyAPIView,
)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='api-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('login/', TokenObtainPairView.as_view(), name='api-login'),

    path('articles/', ArticleListCreateAPIView.as_view(), name='api-articles'),
    path('articles/subscribed/', ArticleSubscribedAPIView.as_view(), name='api-articles-subscribed'),
    path('articles/<int:pk>/', ArticleRetrieveUpdateDestroyAPIView.as_view(), name='api-article-detail'),

    path('approved/', ApprovedWebhookAPIView.as_view(), name='api-approved'),

    path('newsletters/', NewsletterListCreateAPIView.as_view(), name='api-newsletters'),
    path('newsletters/<int:pk>/', NewsletterRetrieveUpdateDestroyAPIView.as_view(), name='api-newsletter-detail'),
]