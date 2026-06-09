from django.contrib import admin

from catalog.forms import ProductForm
from catalog.models import Product, Category, Contact


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "description",
    )

    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    form = ProductForm

    list_display = (
        "id",
        "name",
        "price",
        "category",
        "owner",
        "status",
        "views_count",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "views_count",
    )

    fields = (
        "name",
        "description",
        "image",
        "category",
        "price",
        "owner",
        "status",
        "moderator_comment",
        "views_count",
        "created_at",
        "updated_at",
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "city",
        "phone",
        "email",
    )

    search_fields = (
        "city",
        "email",
    )
