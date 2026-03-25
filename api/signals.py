import requests
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import User, Article, Newsletter


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    if sender.name != 'api':
        return

    reader_group, _ = Group.objects.get_or_create(name='Reader')
    journalist_group, _ = Group.objects.get_or_create(name='Journalist')
    editor_group, _ = Group.objects.get_or_create(name='Editor')

    article_perms = Permission.objects.filter(content_type__app_label='api', content_type__model='article')
    newsletter_perms = Permission.objects.filter(content_type__app_label='api', content_type__model='newsletter')
    approval_perm = Permission.objects.filter(codename='can_approve_article').first()

    reader_group.permissions.set(
        list(article_perms.filter(codename__in=['view_article'])) +
        list(newsletter_perms.filter(codename__in=['view_newsletter']))
    )

    journalist_group.permissions.set(
        list(article_perms.filter(codename__in=['view_article', 'add_article', 'change_article', 'delete_article'])) +
        list(newsletter_perms.filter(codename__in=['view_newsletter', 'add_newsletter', 'change_newsletter', 'delete_newsletter']))
    )

    editor_permissions = list(article_perms.filter(codename__in=['view_article', 'change_article', 'delete_article'])) + \
                         list(newsletter_perms.filter(codename__in=['view_newsletter', 'change_newsletter', 'delete_newsletter']))

    if approval_perm:
        editor_permissions.append(approval_perm)

    editor_group.permissions.set(editor_permissions)


@receiver(post_save, sender=Article)
def send_article_approved(sender, instance, created, **kwargs):
    if instance.approved:
        try:
            requests.post('http://127.0.0.1:8000/api/approved/', json={
                'article_id': instance.id,
                'title': instance.title
            })
        except:
            pass