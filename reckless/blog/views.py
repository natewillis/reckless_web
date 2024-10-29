from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Post, Comment
import markdown

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite'])
        context['content'] = md.convert(self.object.content)
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'slug', 'content', 'featured_image', 'status']
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'slug', 'content', 'featured_image', 'status']

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
