from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from homepage.models import Author, Item
from homepage.urls import *
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from homepage.urls import *
from homepage.models import Item
from homepage.models import Author, Item


class TestHomepage(TestCase):
    def test_url_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse("homepage:home"))
        self.assertEqual(response.status_code, 200)

    def test_url_template(self):
        response = self.client.get(reverse("homepage:home"))
        self.assertTemplateUsed(response, "home_index.html")

    def test_url_template_content(self):
        response = self.client.get(reverse("homepage:home"))
        self.assertContains(response, "<title>UoA DHPA Database Project</title>")
        self.assertNotContains(response, "Not on page")


class TestItemDisplay(TestCase):
    def setUp(self):
        author = Author.objects.create(
            Last_Name="Doe",
            First_Name="John")

        some_authors = [author]
        self.item = Item.objects.create(
            Title="Image Title",
            # Author=author,
            Miniature_Image="media/media",
            Media=1
        )

        self.item.Author.set(some_authors)

    def test_url_location(self):
        response = self.client.get(reverse("homepage:detail_page", kwargs={"pk": self.item.pk}))
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse("homepage:detail_page", kwargs={"pk": self.item.pk}))
        self.assertEqual(response.status_code, 200)

    def test_url_template(self):
        response = self.client.get(reverse("homepage:detail_page", kwargs={"pk": self.item.pk}))
        self.assertTemplateUsed(response, "item_display.html")

    def test_url_template_content(self):
        response = self.client.get(reverse("homepage:detail_page", kwargs={"pk": self.item.pk}))
        self.assertContains(response, "<h1>Image Title</h1>")
        self.assertNotContains(response, "Not on page")


class TestHelpPage(TestCase):
    def test_url_location(self):
        response = self.client.get(reverse("homepage:help_page"))
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse("homepage:help_page"))
        self.assertEqual(response.status_code, 200)

    def test_url_template(self):
        response = self.client.get(reverse("homepage:help_page"))
        self.assertTemplateUsed(response, "help_page.html")

    def test_url_template_content(self):
        response = self.client.get(reverse("homepage:help_page"))
        self.assertContains(response, "<title>Website Help</title>")
        self.assertNotContains(response, "Not on page")


class TestUploadPage(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_url_location(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse("homepage:upload_item"))
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse("homepage:upload_item"))
        self.assertEqual(response.status_code, 200)

    def test_url_template(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse("homepage:upload_item"))
        self.assertTemplateUsed(response, "upload_index.html")

    def test_url_template_content(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse("homepage:upload_item"))
        print(response.content)
        self.assertContains(response, "<h2>Connect With Us</h2>")
        self.assertNotContains(response, "<title>Not on page<title>")
