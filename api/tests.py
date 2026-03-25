from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import User, Publisher, Article, Newsletter
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class APITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create Publisher
        self.publisher_owner = User.objects.create_user(
            username='publisher',
            password='pass123',
            role='publisher'
        )

        self.publisher = Publisher.objects.create(
            user=self.publisher_owner,
            name='Vault News'
        )

        self.publisher_owner.publisher = self.publisher
        self.publisher_owner.save()

        # Create Users
        self.journalist = User.objects.create_user(
            username='journalist',
            password='pass123',
            role='journalist',
            publisher=self.publisher
        )

        self.editor = User.objects.create_user(
            username='editor',
            password='pass123',
            role='editor',
            publisher=self.publisher
        )

        self.reader = User.objects.create_user(
            username='reader',
            password='pass123',
            role='reader'
        )

        # Reader subscribes
        self.reader.subscriptions_publishers.add(self.publisher)

        # Create Article
        self.article = Article.objects.create(
            title="Test Article",
            content="Content",
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

    
    def test_auth_required(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 401)

    
    def test_journalist_can_create_article(self):
        self.client.login(username='journalist', password='pass123')

        response = self.client.post('/api/articles/', {
            'title': 'New Article',
            'content': 'Test',
            'publisher': self.publisher.id
        })

        self.assertEqual(response.status_code, 201)

    def test_reader_cannot_create_article(self):
        self.client.login(username='reader', password='pass123')

        response = self.client.post('/api/articles/', {
            'title': 'Hack',
            'content': 'Nope',
        })

        self.assertEqual(response.status_code, 403)

    def test_reader_sees_only_subscribed_articles(self):
        self.client.login(username='reader', password='pass123')

        self.article.approved = True
        self.article.save()

        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    
    def test_editor_can_approve_article(self):
        self.client.login(username='editor', password='pass123')

        response = self.client.patch(
            f'/api/articles/{self.article.id}/',
            {'approved': True},
            format='json'
        )

        self.article.refresh_from_db()
        self.assertTrue(self.article.approved)

    def test_reader_cannot_approve(self):
        self.client.login(username='reader', password='pass123')

        response = self.client.patch(
            f'/api/articles/{self.article.id}/',
            {'approved': True},
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    
    def test_editor_can_delete_article(self):
        self.client.login(username='editor', password='pass123')

        response = self.client.delete(f'/api/articles/{self.article.id}/')

        self.assertEqual(response.status_code, 204)

    
    def test_newsletter_creation(self):
        self.client.login(username='journalist', password='pass123')

        response = self.client.post('/api/newsletters/', {
            'title': 'Weekly News',
            'description': 'Summary',
            'articles': [self.article.id]
        }, format='json')

        self.assertEqual(response.status_code, 201)