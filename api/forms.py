from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Article, Newsletter, Publisher


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'publisher')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'publisher')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].required = False


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'publisher', 'approved')


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('title', 'description', 'articles', 'publisher')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].required = False


class SubscriptionForm(forms.Form):
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    journalists = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='journalist'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )