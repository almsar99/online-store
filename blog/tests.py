from django.test import TestCase


class BlogSmokeTestCase(TestCase):

    def test_blog_list_page(self):
        response = self.client.get("/blogs/")

        self.assertIn(response.status_code, [200, 302])
