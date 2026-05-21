from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import (
    HomeListView,
    ContactsTemplateView,
    ProductDetailView,
    CategoryProductsListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductUnpublishView,
    ProductPublishView,
    MyProductsListView,
    ModerationListView,
    ProductApproveView,
    ProductRejectView,
)

app_name = CatalogConfig.name

urlpatterns = [
    path(
        '',
        HomeListView.as_view(),
        name='home'
    ),

    path(
        'contacts/',
        ContactsTemplateView.as_view(),
        name='contacts'
    ),

    path(
        'products/<int:pk>/',
        ProductDetailView.as_view(),
        name='product_detail'
    ),

    path(
        'category/<int:category_id>/products/',
        CategoryProductsListView.as_view(),
        name='category_products'
    ),

    path(
        'create/',
        ProductCreateView.as_view(),
        name='product_create'
    ),

    path(
        'update/<int:pk>/',
        ProductUpdateView.as_view(),
        name='product_update'
    ),

    path(
        'delete/<int:pk>/',
        ProductDeleteView.as_view(),
        name='product_delete'
    ),

    path(
        'publish/<int:pk>/',
        ProductPublishView.as_view(),
        name='product_publish'
    ),

    path(
        'unpublish/<int:pk>/',
        ProductUnpublishView.as_view(),
        name='product_unpublish'
    ),

    path(
        'my-products/',
        MyProductsListView.as_view(),
        name='my_products'
    ),

    path(
        'moderation/',
        ModerationListView.as_view(),
        name='moderation_products'
    ),

    path(
        'approve/<int:pk>/',
        ProductApproveView.as_view(),
        name='product_approve'
    ),

    path(
        'reject/<int:pk>/',
        ProductRejectView.as_view(),
        name='product_reject'
    ),
]
