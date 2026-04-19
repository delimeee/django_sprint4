# from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserRegistrationForm
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView,
)


User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.created_at = timezone.now()
        form.instance.author = self.request.user
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = 'pub_date'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = Comment.objects.filter(post=self.get_object())
        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['comments'] = page_obj

        context['form'] = CommentForm()
        return context


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/create.html'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    publication = None

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.publication
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.publication.pk}
        )


class CommentUpdateView(UpdateView):
    model = Comment
    template_name = 'blog/comment.html'


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    ordering = 'id'
    paginate_by = 10


class ProfileUpdateView(UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'email')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = Post.objects.filter(author=self.get_object())
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


# def index(request):
#     template = 'blog/index.html'
#     post_list = Post.objects.select_related(

#     ).filter(
#         pub_date__lte=timezone.now(),
#         is_published=True,
#         category__is_published=True
#     )[:5]
#     context = {
#         'post_list': post_list
#     }
#     return render(request, template, context)


# def post_detail(request, id):
#     template = 'blog/detail.html'
#     post = get_object_or_404(
#         Post.objects.all().filter(
#             pub_date__lte=timezone.now(),
#             is_published=True,
#             category__is_published=True
#         ),
#         pk=id
#     )

#     context = {
#         'post': post
#     }
#     return render(request, template, context)


# def category_posts(request, category_slug):
#     template = 'blog/category.html'
#     category = get_object_or_404(
#         Category,
#         is_published=True,
#         slug=category_slug
#     )
#     posts = Post.objects.select_related().filter(
#         category=category,
#         is_published=True,
#         pub_date__lte=timezone.now()
#     )
#     context = {
#         'category': category,
#         'post_list': posts
#     }
#     return render(request, template, context)
