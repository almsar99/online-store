from django.core.cache import cache

from catalog.models import Product


def get_products_by_category(category_id):
    cache_key = f'category_{category_id}'

    products = cache.get(cache_key)

    if products is None:
        products = list(
            Product.objects.filter(
                category_id=category_id,
                status=Product.STATUS_PUBLISHED
            )
        )

        cache.set(
            cache_key,
            products,
            60 * 15
        )

    return products
