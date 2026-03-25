from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Publisher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_publisher'
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


ROLE_CHOICES = (
    ('reader', 'Reader'),
    ('journalist', 'Journalist'),
    ('editor', 'Editor'),
    ('publisher', 'Publisher'),
)

class User(AbstractUser):
    """
    Allows new users to choose thier role upon registration.
    """
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Reader subscriptions
    subscriptions_publishers = models.ManyToManyField(
        Publisher, blank=True, related_name='subscribed_readers'
    )
    subscriptions_journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        symmetrical=False,
        related_name='subscribed_readers'
    )
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    def __str__(self):
        return self.username


class Article(models.Model):
    """
    Displays article qulities and if approved or not.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_articles'
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
        ],
        default='pending'
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ('can_approve_article', 'Can approve article'),
        ]

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Displays details of newsletter.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newsletters'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    articles = models.ManyToManyField(Article, blank=True, related_name='newsletters')

    def __str__(self):
        return self.title