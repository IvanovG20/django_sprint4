from typing import Any
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import (CreateView, UpdateView,
                                  DeleteView, ListView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Category, Comment, User
from .forms import CommentForm, PostForm

LIMIT_CONST = 5


class IndexListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        posts = Post.objects.select_related(
            'category'
        ).filter(is_published=True,
                 category__is_published=True,
                 pub_date__lte=date.today()
                 ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))
        return posts


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        if not self.request.user.is_authenticated or (
            post.author != self.request.user
        ):
            post = get_object_or_404(
                Post,
                is_published=True,
                id=self.kwargs['post_id'],
                pub_date__lte=date.today(),
                category__is_published=True,
            )
            return post
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related(
                'author'
            )
        )
        return context


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug,
    )
    post_list = category.posts(
        manager='post_objects'
    ).annotate(
        comment_count=Count('comment')
    ).all()
    post_list = post_list.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html', {'category': category,
                                                  'page_obj': page_obj, })


class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )

    def get_context_data(self, **kwargs: Any):
        return super().get_context_data(**kwargs)


class PostsUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.kwargs['post_id']
            }
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10
    pk_url_kwarg = 'username'

    def get_queryset(self):
        self.author = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return Post.objects.select_related(
            'author',
            'location',
            'category',
        ).filter(author=self.author).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']})


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']})
