# from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView,
)


User = get_user_model()


class OwnershipRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect("blog:post_detail", post_id=obj.id)
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.created_at = timezone.now()
        form.instance.author = self.request.user
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostListView(ListView):
    model = Post
    template_name = "blog/index.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_queryset(self):
        qs = Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

        if self.request.user.is_authenticated:
            qs = qs | Post.objects.filter(author=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = Comment.objects.filter(
            post=self.get_object()).order_by("created_at")
        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["comments"] = page_obj

        context["form"] = CommentForm()
        return context


class PostUpdateView(LoginRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.id}
        )


class PostDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("blog:index")


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    publication = None

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.publication
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.publication.pk}
        )


class CommentUpdateView(
        LoginRequiredMixin,
        OwnershipRequiredMixin,
        UpdateView):
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm
    pk_url_kwarg = "comment_id"

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.post.id}
        )


class CommentDeleteView(
        LoginRequiredMixin,
        OwnershipRequiredMixin,
        DeleteView):
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.post.id}
        )


class CategoryListView(ListView):
    model = Post
    template_name = "blog/category.html"
    paginate_by = 10
    category = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return context

    def get_queryset(self):
        return (
            Post.objects.filter(
                category__slug=self.kwargs["category_slug"],
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    fields = ("first_name", "last_name", "email")

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class ProfileDetailView(DetailView):
    model = User
    template_name = "blog/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user == self.get_object():
            posts = (
                Post.objects.filter(author=self.get_object())
                .annotate(comment_count=Count("comments"))
                .order_by("-pub_date")
            )
        else:
            posts = (
                Post.objects.filter(
                    author=self.get_object(),
                    is_published=True,
                    pub_date__lte=timezone.now(),
                    category__is_published=True,
                )
                .annotate(comment_count=Count("comments"))
                .order_by("-pub_date")
            )

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context
