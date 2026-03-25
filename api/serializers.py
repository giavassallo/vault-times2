from rest_framework import serializers
from .models import Article, Newsletter, Publisher, User


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name', 'description')


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'role')


class ArticleSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)
    publisher = serializers.PrimaryKeyRelatedField(queryset=Publisher.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'author', 'publisher', 'created_at', 'updated_at', 'approved')


class NewsletterSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)
    articles = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all(), many=True, required=False)

    class Meta:
        model = Newsletter
        fields = ('id', 'title', 'description', 'author', 'created_at', 'articles')