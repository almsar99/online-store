from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from blog.models import Blog


class BlogListView(ListView):

    model = Blog

    template_name = 'blog/blog_list.html'

    context_object_name = 'blogs'

    queryset = Blog.objects.filter(is_published=True)


class BlogDetailView(DetailView):

    model = Blog

    template_name = 'blog/blog_detail.html'

    context_object_name = 'blog'

    def get_object(self, queryset=None):

        self.object = super().get_object(queryset)

        self.object.views_count += 1

        self.object.save()

        return self.object


class BlogCreateView(LoginRequiredMixin, CreateView):

    model = Blog

    fields = (
        'title',
        'content',
        'preview',
        'is_published',
    )

    template_name = 'blog/blog_form.html'

    success_url = reverse_lazy('blog:list')

    def dispatch(self, request, *args, **kwargs):

        if not request.user.has_perm('blog.can_manage_blog'):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class BlogUpdateView(LoginRequiredMixin, UpdateView):

    model = Blog

    fields = (
        'title',
        'content',
        'preview',
        'is_published',
    )

    template_name = 'blog/blog_form.html'

    success_url = reverse_lazy('blog:list')

    def dispatch(self, request, *args, **kwargs):

        if not request.user.has_perm('blog.can_manage_blog'):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class BlogDeleteView(LoginRequiredMixin, DeleteView):

    model = Blog

    template_name = 'blog/blog_confirm_delete.html'

    success_url = reverse_lazy('blog:list')

    def dispatch(self, request, *args, **kwargs):

        if not request.user.has_perm('blog.can_manage_blog'):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
