from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, ArticleCreateForm, ArticleEditForm, NewsletterForm, SubscriptionForm
from .models import Article, Newsletter, Publisher, User


def login_view(request):
    """
    Allows registered users to login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')   
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


def logout_view(request):
    """"
    Allows logged in users to logout
    """
    logout(request)
    return redirect('login')


def home(request):
    """
    Home page of application
    """
    return render(request, 'home.html')


def register_view(request):
    """
    Allows new users to register.
    Users can choose their roles.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            if user.role == 'publisher':
                publisher = Publisher.objects.create(
                    user=user,
                    name=user.username
                )
                user.publisher = publisher
                user.save()

            login(request, user)
            return redirect('home')   
        else:
            print(form.errors) 

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    """
    Displays dashboard according to user.
    """
    if request.user.role == 'reader':
        return redirect('reader-dashboard')
    if request.user.role == 'journalist':
        return redirect('journalist-dashboard')
    if request.user.role == 'editor':
        return redirect('editor-dashboard')
    if request.user.role == 'publisher':  
        return redirect('publisher-dashboard')
    return redirect('home')


@login_required
def reader_dashboard(request):
    """
    Dashboard for reader only.
    Readers can view subscription articles and newsletters.
    Readers can subscribe to publishers and journalists.
    """
    if request.user.role != 'reader':
        return HttpResponseForbidden()
    subscribed_articles = Article.objects.filter(
        approved=True
    ).filter(
        Q(author__in=request.user.subscriptions_journalists.all()) |
        Q(publisher__in=request.user.subscriptions_publishers.all())
    ).distinct().order_by('-created_at')
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'dashboards/reader.html', {
        'subscribed_articles': subscribed_articles,
        'newsletters': newsletters,
    })


@login_required
def journalist_dashboard(request):
    """
    Displays journalist dashboard.
    Journalists can create, edit, delete articles and newsletters.
    """
    if request.user.role != 'journalist':
        return HttpResponseForbidden()
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    newsletters = Newsletter.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'dashboards/journalist.html', {
        'articles': articles,
        'newsletters': newsletters,
    })


@login_required
def editor_dashboard(request):
    """
    Displays editor dashboard.
    Editors can apprve articles and view arrpoval queue.
    Editors can edit, create, delete articles and newsletters
    """
    if request.user.role != 'editor':
        return HttpResponseForbidden()
    queue = Article.objects.filter(approved=False).order_by('-created_at')
    return render(request, 'dashboards/editor.html', {'queue': queue})


@login_required
def publisher_dashboard(request):
    """
    Displays publisher dashboard.
    Publishers can view articles and news letters under them.
    """
    if request.user.role != 'publisher':
        return HttpResponseForbidden()

    publisher = request.user.publisher

    articles = Article.objects.filter(publisher=publisher)
    newsletters = Newsletter.objects.filter(publisher=request.user.publisher)
    journalists = User.objects.filter(role='journalist', publisher=publisher)
    editors = User.objects.filter(role='editor', publisher=publisher)

    return render(request, 'dashboards/publisher.html', {
        'articles': articles,
        'newsletters': newsletters,
        'journalists': journalists,
        'editors': editors,
    })


@login_required
def article_list(request):
    """
    Displays list of articles per role.
    """
    if request.user.role == 'reader':
        articles = Article.objects.filter(
            approved=True
        ).filter(
            Q(author__in=request.user.subscriptions_journalists.all()) |
            Q(publisher__in=request.user.subscriptions_publishers.all())
        ).distinct().order_by('-created_at')
    elif request.user.role == 'journalist':
        articles = Article.objects.filter(author=request.user).order_by('-created_at')
    else:
        articles = Article.objects.all().order_by('-created_at')
    return render(request, 'articles/list.html', {'articles': articles})


@login_required
def article_detail(request, pk):
    """
    Displays article detail per role."""
    article = get_object_or_404(Article, pk=pk)

    allowed = False
    if request.user.role == 'editor':
        allowed = True
    elif request.user.role == 'journalist':
        allowed = article.author == request.user or article.approved
    elif request.user.role == 'reader':
        allowed = article.approved and (
            article.author in request.user.subscriptions_journalists.all() or
            article.publisher in request.user.subscriptions_publishers.all()
        )

    if not allowed:
        return HttpResponseForbidden()

    return render(request, 'articles/detail.html', {'article': article})


@login_required
def create_article(request):
    """
    Allows journalists and editors to create articles.
    """
    if request.user.role != 'journalist':
        return redirect('home')

    if request.method == 'POST':
        form = ArticleCreateForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.publisher = request.user.publisher
            article.save()
            return redirect('home')
    else:
        form = ArticleCreateForm()

    return render(request, 'articles/create.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def article_edit(request, pk):
    """
    Allows editors and journalists to edit articles.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.role != 'editor' and article.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ArticleEditForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated.')
            return redirect('article-detail', pk=article.pk)
    else:
        form = ArticleEditForm(instance=article)

    return render(request, 'articles/form.html', {'form': form, 'title': 'Edit Article'})


@login_required
@require_http_methods(["GET", "POST"])
def article_delete(request, pk):
    """
    Allows editors and journalists to delete articles.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.role != 'editor' and article.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted.')
        return redirect('article-list')

    return render(request, 'articles/confirm_delete.html', {'article': article})


@login_required
def approval_queue(request):
    """
    Displays approval queue for editors.
    """
    if request.user.role != 'editor':
        return HttpResponseForbidden()
    queue = Article.objects.filter(approved=False).order_by('-created_at')
    return render(request, 'approvals/queue.html', {'queue': queue})


@login_required
def approve_article(request, pk):
    """
    Allows editor to approve articles.
    """
    article = get_object_or_404(Article, pk=pk)
    
    if request.user.role != 'editor':
        return HttpResponseForbidden()

    if request.method == "POST":
        article.approved = True
        article.save()
        print("APPROVED:", article.id)

    return redirect('approve')


@login_required
def view_articles(request):
    """
    Displays view of articles.
    """
    articles = Article.objects.filter(approved=True)
    return render(request, 'articles.html', {'articles': articles})


@login_required
def newsletter_list(request):
    """
    Displays list of newsletters.
    """
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'newsletters/list.html', {'newsletters': newsletters})


@login_required
def newsletter_detail(request, pk):
    """
    Newsletter details display.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(request, 'newsletters/detail.html', {'newsletter': newsletter})


@login_required
@require_http_methods(["GET", "POST"])
def newsletter_create(request):
    """
    Allows journalists and editors to create newsletters.
    """
    if request.user.role not in ('journalist', 'editor'):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user

            newsletter.publisher = form.cleaned_data.get('publisher')

            newsletter.save()
            form.save_m2m()

            messages.success(request, 'Newsletter created.')
            return redirect('newsletter-list')
    else:
        form = NewsletterForm()

    return render(request, 'newsletters/form.html', {'form': form, 'title': 'Create Newsletter'})


@login_required
@require_http_methods(["GET", "POST"])
def newsletter_edit(request, pk):
    """
    Allows journalists and editors to edit newsletters.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.user.role != 'editor' and newsletter.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter updated.')
            return redirect('newsletter-detail', pk=newsletter.pk)
    else:
        form = NewsletterForm(instance=newsletter)

    return render(request, 'newsletters/form.html', {'form': form, 'title': 'Edit Newsletter'})


@login_required
@require_http_methods(["GET", "POST"])
def newsletter_delete(request, pk):
    """
    Allows journalists and editors to delete newsletters.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.user.role != 'editor' and newsletter.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted.')
        return redirect('newsletter-list')

    return render(request, 'newsletters/confirm_delete.html', {'newsletter': newsletter})


@login_required
def manage_subscriptions(request):
    """
    Allows reader to add, edit and view subscriptions.
    """
    if request.user.role != 'reader':
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            request.user.subscriptions_publishers.set(form.cleaned_data['publishers'])
            request.user.subscriptions_journalists.set(form.cleaned_data['journalists'])
            messages.success(request, 'Subscriptions saved.')
            return redirect('reader-dashboard')
    else:
        form = SubscriptionForm(initial={
            'publishers': request.user.subscriptions_publishers.all(),
            'journalists': request.user.subscriptions_journalists.all(),
        })

    return render(request, 'subscriptions/manage.html', {'form': form})