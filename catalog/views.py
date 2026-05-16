from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from catalog.forms import ProductForm
from catalog.models import Product, Contact


class HomeListView(ListView):

    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'

    def get_queryset(self):

        return Product.objects.all().order_by('id')

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.object_list, 2)

        page_number = self.request.GET.get('page')

        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj

        return context


class ContactsTemplateView(TemplateView):

    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['contacts_list'] = Contact.objects.all()

        return context


class ProductDetailView(DetailView):

    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):

        self.object = super().get_object(queryset)

        self.object.views_count += 1

        self.object.save()

        return self.object


class ProductCreateView(LoginRequiredMixin, CreateView):

    model = Product

    form_class = ProductForm

    template_name = 'catalog/product_form.html'

    success_url = reverse_lazy('catalog:home')

    login_url = '/users/login/'

    def form_valid(self, form):

        form.instance.owner = self.request.user

        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):

    model = Product

    form_class = ProductForm

    template_name = 'catalog/product_form.html'

    login_url = '/users/login/'

    def dispatch(self, request, *args, **kwargs):

        product = self.get_object()

        if (
            product.owner != request.user
            and not request.user.has_perm(
                'catalog.can_unpublish_product'
            )
        ):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):

        return reverse_lazy(
            'catalog:product_detail',
            args=[self.kwargs.get('pk')]
        )


class ProductDeleteView(LoginRequiredMixin, DeleteView):

    model = Product

    template_name = 'catalog/product_confirm_delete.html'

    success_url = reverse_lazy('catalog:home')

    login_url = '/users/login/'

    def dispatch(self, request, *args, **kwargs):

        product = self.get_object()

        if (
            product.owner != request.user
            and not request.user.has_perm(
                'catalog.delete_product'
            )
        ):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
