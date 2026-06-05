from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from catalog.forms import ProductForm
import catalog.services as catalog_services

User = get_user_model()


class CatalogPagesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="catalog_user@example.com",
            password="test_password_123",
            is_active=True,
        )
        self.category = Category.objects.create(
            name="Тестовая категория",
            description="Описание тестовой категории",
        )
        self.product = Product.objects.create(
            name="Тестовый товар",
            description="Описание тестового товара",
            price=100,
            category=self.category,
            owner=self.user,
        )

    def test_home_page_is_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_contacts_page_is_available(self):
        response = self.client.get("/contacts/")

        self.assertEqual(response.status_code, 200)

    def test_home_url_name_is_available(self):
        response = self.client.get(reverse("catalog:home"))

        self.assertEqual(response.status_code, 200)

    def test_product_model_creation(self):
        self.assertEqual(self.product.name, "Тестовый товар")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.owner, self.user)

    def test_my_products_requires_authentication(self):
        response = self.client.get(reverse("catalog:my_products"))

        self.assertEqual(response.status_code, 302)

    def test_my_products_page_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("catalog:my_products"))

        self.assertEqual(response.status_code, 200)

    def test_product_create_requires_authentication(self):
        response = self.client.get(reverse("catalog:product_create"))

        self.assertEqual(response.status_code, 302)

    def test_product_create_page_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("catalog:product_create"))

        self.assertEqual(response.status_code, 200)


class CatalogServicesTestCase(TestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            email="service_user@example.com",
            password="test_password_123",
            is_active=True,
        )
        self.category = Category.objects.create(
            name="Категория кеша",
            description="Описание категории кеша",
        )
        self.product = Product.objects.create(
            name="Товар кеша",
            description="Описание товара кеша",
            price=500,
            category=self.category,
            owner=self.user,
        )

        self.publish_product_for_service_tests()

    def publish_product_for_service_tests(self):
        product_fields = {field.name for field in Product._meta.fields}
        updated_fields = []

        if "is_published" in product_fields:
            self.product.is_published = True
            updated_fields.append("is_published")

        if "is_active" in product_fields:
            self.product.is_active = True
            updated_fields.append("is_active")

        published_status = getattr(
            Product,
            "STATUS_PUBLISHED",
            "published",
        )

        for status_field in (
            "status",
            "publication_status",
            "moderation_status",
        ):
            if status_field in product_fields:
                setattr(
                    self.product,
                    status_field,
                    published_status,
                )
                updated_fields.append(status_field)

        if updated_fields:
            self.product.save(
                update_fields=updated_fields,
            )

    def get_cached_products(self):
        for function_name in (
            "get_products_from_cache",
            "get_products_by_category",
            "get_product_list_by_category",
            "get_cached_products",
        ):
            service_function = getattr(
                catalog_services,
                function_name,
                None,
            )

            if service_function is not None:
                return service_function(self.category.pk)

        self.fail("Catalog cache service function was not found.")

    def test_get_products_from_cache_returns_category_products(self):
        products = self.get_cached_products()

        self.assertIn(
            self.product,
            products,
        )

    def test_get_products_from_cache_saves_data_to_cache(self):
        cache_key = f"category_{self.category.pk}"

        self.assertIsNone(
            cache.get(cache_key),
        )

        self.get_cached_products()

        self.assertIsNotNone(
            cache.get(cache_key),
        )


class CatalogProductFormTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Категория формы",
            description="Описание категории формы",
        )

    def get_valid_form_data(self):
        return {
            "name": "Обычный товар",
            "description": "Описание обычного товара",
            "category": self.category.pk,
            "price": 100,
        }

    def test_product_form_is_valid_with_correct_data(self):
        form = ProductForm(data=self.get_valid_form_data())

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

    def test_product_form_adds_bootstrap_class_to_fields(self):
        form = ProductForm()

        for field in form.fields.values():
            self.assertEqual(
                field.widget.attrs.get("class"),
                "form-control",
            )

    def test_product_form_rejects_forbidden_word_in_name(self):
        form_data = self.get_valid_form_data()
        form_data["name"] = "Дешево купить товар"

        form = ProductForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Название содержит запрещенное слово.",
            form.errors["__all__"],
        )

    def test_product_form_rejects_forbidden_word_in_description(self):
        form_data = self.get_valid_form_data()
        form_data["description"] = "Товар бесплатно для всех"

        form = ProductForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Описание содержит запрещенное слово.",
            form.errors["__all__"],
        )

    def test_product_form_rejects_negative_price(self):
        form_data = self.get_valid_form_data()
        form_data["price"] = -10

        form = ProductForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Цена не может быть отрицательной.",
            form.errors["price"],
        )

    def test_product_form_rejects_wrong_image_extension(self):
        form_data = self.get_valid_form_data()
        uploaded_file = SimpleUploadedFile(
            "document.txt",
            b"not image content",
            content_type="text/plain",
        )

        form = ProductForm(
            data=form_data,
            files={"image": uploaded_file},
        )

        self.assertFalse(form.is_valid())
