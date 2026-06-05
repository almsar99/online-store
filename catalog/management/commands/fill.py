import json

from django.core.management import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):

    def handle(self, *args, **options):

        Product.objects.all().delete()
        Category.objects.all().delete()

        with open("catalog/fixtures/category.json", "r", encoding="utf-8") as file:
            categories = json.load(file)

            for category in categories:
                Category.objects.create(
                    id=category["pk"],
                    name=category["fields"]["name"],
                    description=category["fields"]["description"],
                )

        with open("catalog/fixtures/product.json", "r", encoding="utf-8") as file:
            products = json.load(file)

            for product in products:
                category = Category.objects.get(pk=product["fields"]["category"])

                Product.objects.create(
                    id=product["pk"],
                    name=product["fields"]["name"],
                    description=product["fields"]["description"],
                    price=product["fields"]["price"],
                    category=category,
                    created_at=product["fields"]["created_at"],
                    updated_at=product["fields"]["updated_at"],
                )
