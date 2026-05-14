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

    def get_queryset(self):
        return Blog.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        obj.views_count += 1
        obj.save()

        return obj


class BlogCreateView(CreateView):
    model = Blog
    fields = (
        'title',
        'content',
        'preview',
        'is_published',
    )
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:list')


class BlogUpdateView(UpdateView):
    model = Blog
    fields = (
        'title',
        'content',
        'preview',
        'is_published',
    )
    template_name = 'blog/blog_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:view',
            args=[self.kwargs.get('pk')]
        )


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:list')
