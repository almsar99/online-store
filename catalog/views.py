from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.urls import reverse_lazy
from django.views import View
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
from catalog.services import get_products_by_category


class HomeListView(ListView):

    model = Product

    template_name = "catalog/home.html"

    context_object_name = "page_obj"

    def get_queryset(self):

        return Product.objects.filter(status=Product.STATUS_PUBLISHED).order_by("id")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.object_list, 2)

        page_number = self.request.GET.get("page")

        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj

        return context


class ContactsTemplateView(TemplateView):

    template_name = "catalog/contacts.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["contacts_list"] = Contact.objects.all()

        return context


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProductDetailView(DetailView):

    model = Product

    template_name = "catalog/product_detail.html"

    context_object_name = "product"

    def get_object(self, queryset=None):

        self.object = super().get_object(queryset)

        self.object.views_count += 1

        self.object.save()

        return self.object


class CategoryProductsListView(ListView):

    model = Product

    template_name = "catalog/category_products.html"

    context_object_name = "products"

    def get_queryset(self):

        return get_products_by_category(self.kwargs.get("category_id"))

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["category_id"] = self.kwargs.get("category_id")

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):

    model = Product

    form_class = ProductForm

    template_name = "catalog/product_form.html"

    success_url = reverse_lazy("catalog:home")

    login_url = "/users/login/"

    def form_valid(self, form):

        form.instance.owner = self.request.user

        form.instance.status = Product.STATUS_DRAFT

        form.instance.moderator_comment = ""

        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):

    model = Product

    form_class = ProductForm

    template_name = "catalog/product_form.html"

    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):

        product = self.get_object()

        if product.owner != request.user:

            raise PermissionDenied

        # редактировать опубликованный товар нельзя
        if product.status == Product.STATUS_PUBLISHED:

            messages.error(
                request, "Редактировать можно только снятые с публикации товары"
            )

            return redirect("catalog:my_products")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        product = form.save(commit=False)

        # после редактирования товар снова становится черновиком
        product.status = Product.STATUS_DRAFT

        # очищаем комментарий модератора
        product.moderator_comment = ""

        product.save()

        return redirect("catalog:product_detail", pk=product.pk)

    def get_success_url(self):

        return reverse_lazy("catalog:product_detail", args=[self.kwargs.get("pk")])


class ProductDeleteView(LoginRequiredMixin, DeleteView):

    model = Product

    template_name = "catalog/product_confirm_delete.html"

    success_url = reverse_lazy("catalog:home")

    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):

        product = self.get_object()

        if product.owner != request.user and not request.user.has_perm(
            "catalog.delete_product"
        ):

            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class ProductUnpublishView(LoginRequiredMixin, View):

    login_url = "/users/login/"

    def post(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        if product.owner != request.user and not request.user.has_perm(
            "catalog.can_unpublish_product"
        ):

            raise PermissionDenied

        comment = request.POST.get("moderator_comment")

        # снимаем с публикации
        product.status = Product.STATUS_DRAFT

        if request.user.has_perm("catalog.can_unpublish_product"):

            product.moderator_comment = comment

            product.save(
                update_fields=[
                    "status",
                    "moderator_comment",
                ]
            )

        else:

            product.save(update_fields=["status"])

        return redirect("catalog:my_products")


class ProductPublishView(LoginRequiredMixin, View):

    login_url = "/users/login/"

    def post(self, request, pk):

        product = get_object_or_404(Product, pk=pk)

        if product.owner != request.user and not request.user.has_perm(
            "catalog.can_unpublish_product"
        ):

            raise PermissionDenied

        # модератор публикует сразу
        if request.user.has_perm("catalog.can_unpublish_product"):

            product.status = Product.STATUS_PUBLISHED

        # обычный пользователь отправляет на модерацию
        else:

            product.status = Product.STATUS_PENDING

        product.save(update_fields=["status"])

        return redirect("catalog:my_products")


class MyProductsListView(LoginRequiredMixin, ListView):

    model = Product

    template_name = "catalog/my_products.html"

    context_object_name = "products"

    login_url = "/users/login/"

    def get_queryset(self):

        return Product.objects.filter(owner=self.request.user).order_by("-id")


class ModerationListView(LoginRequiredMixin, ListView):

    model = Product

    template_name = "catalog/moderation_products.html"

    context_object_name = "products"

    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):

        if not request.user.has_perm("catalog.can_unpublish_product"):

            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return Product.objects.filter(status=Product.STATUS_PENDING).order_by("-id")


class ProductApproveView(LoginRequiredMixin, View):

    login_url = "/users/login/"

    def post(self, request, pk):

        if not request.user.has_perm("catalog.can_unpublish_product"):

            raise PermissionDenied

        product = get_object_or_404(Product, pk=pk)

        product.status = Product.STATUS_PUBLISHED

        product.moderator_comment = ""

        product.save(
            update_fields=[
                "status",
                "moderator_comment",
            ]
        )

        return redirect("catalog:moderation_products")


class ProductRejectView(LoginRequiredMixin, View):

    login_url = "/users/login/"

    def post(self, request, pk):

        if not request.user.has_perm("catalog.can_unpublish_product"):

            raise PermissionDenied

        product = get_object_or_404(Product, pk=pk)

        comment = request.POST.get("moderator_comment")

        product.status = Product.STATUS_REJECTED

        product.moderator_comment = comment

        product.save(
            update_fields=[
                "status",
                "moderator_comment",
            ]
        )

        return redirect("catalog:moderation_products")
