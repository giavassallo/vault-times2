from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from rest_framework.exceptions import PermissionDenied
from .models import Article, Newsletter
from .serializers import ArticleSerializer, NewsletterSerializer
from .permissions import IsJournalist, IsEditor, IsJournalistOrEditor, CanModifyArticle, CanModifyNewsletter

from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(approved=True).select_related('author', 'publisher').order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsJournalist()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, approved=False)


class ArticleSubscribedAPIView(ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Article.objects.filter(
            approved=True
        ).filter(
            models.Q(publisher__in=user.subscriptions_publishers.all()) |
            models.Q(author__in=user.subscriptions_journalists.all())
        )


class ArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Article.objects.all()

    def get_queryset(self):
        user = self.request.user

        if user.role == 'editor':
            return Article.objects.all()

        if user.role == 'journalist':
            return Article.objects.filter(
                Q(author=user) | Q(approved=True)
            ).distinct()

        return Article.objects.all()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.request.user

        if 'approved' in serializer.validated_data:
            if user.role != 'editor':
                raise PermissionDenied("Only editors can approve articles")

        serializer.save()


class ApprovedWebhookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'status': 'approved webhook received'}, status=status.HTTP_200_OK)


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Newsletter.objects.all().select_related('author').prefetch_related('articles').order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsJournalistOrEditor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NewsletterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NewsletterSerializer
    queryset = Newsletter.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), CanModifyNewsletter()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.request.user

        if 'approved' in serializer.validated_data:
            if user.role != 'editor':
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Only editors can approve articles")

        serializer.save()