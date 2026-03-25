from django.contrib import admin
from .models import User, Publisher, Article, Newsletter


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'publisher')
    list_filter = ('role',)
    search_fields = ('username',)


class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'publisher')
    search_fields = ('title',)


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'created_at')
    search_fields = ('title',)


admin.site.register(User, UserAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Newsletter, NewsletterAdmin)