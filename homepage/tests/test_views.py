from django.test import TestCase, RequestFactory, Client
from homepage.models import Author, Item, Item_Image, _FileType
from homepage.views import detail_page, searchFunction, sortFunction, home, uploadItemFunction, uploadImageFunction
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
from homepage.models import Approve_Record
import os
from django.core.files.uploadedfile import SimpleUploadedFile


class SearchPageTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            Last_Name="Doe",
            First_Name="John"
        )

        self.item0 = Item.objects.create(
            Title="Image Title 0",
            Miniature_Image="test_miniatureImg0.jpg",
            Upload_Date="2024-04-01",
            Media=1
        )
        self.item0.Author.add(self.author)  # 使用 add 方法
        self.item0.save()

        self.image = Item_Image.objects.create(
            Item=self.item0,
            Image="test_image.jpg",
            View_Detail="Test View Detail",
            Index=1
        )

        self.item1 = Item.objects.create(
            Title="Image Title 1",
            Miniature_Image="test_miniatureImg1.jpg",
            Upload_Date="2024-04-04",
            Media=1
        )
        self.item1.Author.add(self.author)  # 使用 add 方法
        self.item1.save()

        self.item2 = Item.objects.create(
            Title="Image Title 2",
            Miniature_Image="test_minitureImg2.jpg",
            Upload_Date="2024-04-10",
            Media=1
        )
        self.item2.Author.add(self.author)  # 使用 add 方法
        self.item2.save()

        self.item3 = Item.objects.create(
            Title="Image Title 3",
            Miniature_Image="test_minitureImg3.jpg",
            Upload_Date="2024-04-14",
            Media=1
        )
        self.item3.Author.add(self.author)  # 使用 add 方法
        self.item3.save()

        self.image1 = Item_Image.objects.create(
            Item=self.item1,
            Image="test_image1.jpg",
            View_Detail="Test View Detail 1",
            Index=1
        )
        self.image2 = Item_Image.objects.create(
            Item=self.item2,
            Image="test_image2.jpg",
            View_Detail="Test View Detail 2",
            Index=1
        )
        self.image3 = Item_Image.objects.create(
            Item=self.item3,
            Image="test_image3.jpg",
            View_Detail="Test View Detail 3",
            Index=1
        )

        self.search_condition = {
            "title": "Image Title 2",
            "files_Still_Images": "",
            "file_RTI": "",
            "datefrom": "2024-04-10",
            "dateto": "2024-04-11",
            "author": "John Doe",
        }

    def test_results_items(self):
        filtered_data = searchFunction(Item.objects.all(), self.search_condition)
        self.assertEqual(len(filtered_data[1]), 1)

    def test_results_title(self):
        filtered_data = searchFunction(Item.objects.all(), self.search_condition)
        self.assertEqual(filtered_data[1][0].Title, "Image Title 2")

    def test_results_minitureImg(self):
        filtered_data = searchFunction(Item.objects.all(), self.search_condition)
        self.assertEqual(filtered_data[1][0].Miniature_Image, "test_minitureImg2.jpg")

    def test_results_media(self):
        filtered_data = searchFunction(Item.objects.all(), self.search_condition)
        self.assertEqual(filtered_data[1][0].Media, 1)

    def test_results_date(self):
        filtered_data = searchFunction(Item.objects.all(), self.search_condition)
        self.assertEqual(str(filtered_data[1][0].Upload_Date), "2024-04-10")


class SortFunctionTest(TestCase):
    def setUp(self):
        self.author0 = Author.objects.create(
            Last_Name="Doe",
            First_Name="John",
        )
        self.author1 = Author.objects.create(
            Last_Name="John",
            First_Name="John",
        )
        self.author2 = Author.objects.create(
            Last_Name="Johnston",
            First_Name="John",
        )
        self.author3 = Author.objects.create(
            Last_Name="name",
            First_Name="test",
        )

        self.item0 = Item.objects.create(
            Title="Image Title 0",
            Miniature_Image="test_miniatureImg0.jpg",
            Upload_Date="2023-04-01",
            Media=1
        )

        self.item0.Author.set([self.author0])
        self.item0.save()
        self.image = Item_Image.objects.create(
            Item=self.item0,
            Image="test_image.jpg",
            View_Detail="Test View Detail",
            Index=1
        )

        self.item1 = Item.objects.create(
            Title="Image Title 1",
            Miniature_Image="test_miniatureImg1.jpg",
            Upload_Date="2024-04-04",
            Media=1,
        )

        self.item1.Author.set([self.author1])
        self.item1.save()
        self.item2 = Item.objects.create(
            Title="Image Title 2",
            Miniature_Image="test_minitureImg2.jpg",
            Upload_Date="2025-04-10",
            Media=1,
        )

        self.item2.Author.set([self.author2])
        self.item2.save()
        self.item3 = Item.objects.create(
            Title="Image Title 3",
            Miniature_Image="test_minitureImg3.jpg",
            Upload_Date="2026-04-14",
            Media=1,
        )

        self.item3.Author.set([self.author3])
        self.item3.save()
        self.image1 = Item_Image.objects.create(
            Item=self.item1,
            Image="test_image1.jpg",
            View_Detail="Test View Detail 1",
            Index=1
        )
        self.image2 = Item_Image.objects.create(
            Item=self.item2,
            Image="test_image2.jpg",
            View_Detail="Test View Detail 2",
            Index=1
        )
        self.image3 = Item_Image.objects.create(
            Item=self.item3,
            Image="test_image3.jpg",
            View_Detail="Test View Detail 3",
            Index=1
        )

    def test_sort_year_old_to_new(self):
        data = Item.objects.all()
        sortFunction_data = sortFunction(data, "date-old-to-new")
        expected_data = [Item.objects.get(Title=title) for title in
                         ["Image Title 0", "Image Title 1", "Image Title 2", "Image Title 3"]]
        self.assertEqual(list(sortFunction_data), expected_data)

    def test_sort_year_desc(self):
        data = Item.objects.all()
        sortFunction_data = sortFunction(data, "date-new-to-old")
        print("sorted dates:", list(data.order_by("-Upload_Date")))
        expected_data = [Item.objects.get(Title=title) for title in
                         ["Image Title 3", "Image Title 2", "Image Title 1", "Image Title 0"]]
        print("recieved dates:", sortFunction_data)
        self.assertEqual(expected_data, list(sortFunction_data))

    def test_sort_author_asc(self):
        data = Item.objects.all()
        sortFunction_data = sortFunction(data, "author-asc")
        expected_data = [Item.objects.get(Title=title) for title in
                         ["Image Title 0", "Image Title 1", "Image Title 2", "Image Title 3"]]
        self.assertEqual(expected_data, list(sortFunction_data))

    def test_sort_title_asc(self):
        data = Item.objects.all()
        sortFunction_data = sortFunction(data, "title-asc")
        expected_data = [Item.objects.get(Title=title) for title in
                         ["Image Title 0", "Image Title 1", "Image Title 2", "Image Title 3"]]
        self.assertEqual(expected_data, list(sortFunction_data))

    def test_sort_title_des(self):
        data = Item.objects.all()
        sortFunction_data = sortFunction(data, "title-des")
        expected_data = [Item.objects.get(Title=title) for title in
                         ["Image Title 3", "Image Title 2", "Image Title 1", "Image Title 0"]]
        self.assertEqual(expected_data, list(sortFunction_data))


class UploadItemFunctionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser', password='12345')
    def test_uploadItemFunction(self):
        authorNames = ["Author1", "Author2"]
        title = "Sample Title"
        images = ["image1.jpg", "image2.jpg"]
        uploadDate = "2024-07-24"
        Uploader = self.user
        description = "Description of the item"
        alternateTitle = "Alternate Title"
        tags = ["tag1", "tag2"]
        language = "English"
        provenance = "Provenance info"
        currentCollectionLocation = "Collection Location"
        dimensions = "Dimensions info"
        accessionNumber = "Accession Number"
        bibliography = "Bibliography info"
        details = ["Detail1", "Detail2"]
        rtiComp = None
        rtiFilePath = None

        new_item = uploadItemFunction(
            authorNames=authorNames,
            title=title,
            images=images,
            uploadDate=uploadDate,
            Uploader=Uploader,
            description=description,
            alternateTitle=alternateTitle,
            tags=tags,
            language=language,
            provenance=provenance,
            currentCollectionLocation=currentCollectionLocation,
            dimensions=dimensions,
            accessionNumber=accessionNumber,
            bibliography=bibliography,
            details=details,
            rtiComp=rtiComp,
            rtiFilePath=rtiFilePath
        )

        self.assertIsInstance(new_item, Item)
        self.assertEqual(new_item.Title, title)
        self.assertEqual(new_item.Media, len(images))
        item_images = Item_Image.objects.filter(Item=new_item)
        self.assertEqual(len(item_images), len(images))
        imagesList = enumerate(item_images)
        for i, item_image in imagesList:
            index = i + 1
            self.assertEqual(item_image.View_Detail, details[i])
            self.assertEqual(item_image.Index, index)


class UploadImageFunctionTests(TestCase):
    def setUp(self):
        author = Author.objects.create(
            Last_Name="Doe",
            First_Name="John",
        )
        self.item = Item.objects.create(
            Title="Image Title",
            Miniature_Image="miniture.jpg",
            Media=1
        )

        self.item.Author.set([author])

    def test_uploadImageFunction(self):
        image = 'test_image.jpg'
        detail = 'Test Detail'
        index = 1

        item_image = uploadImageFunction(self.item, image, detail, index)
        self.assertIsInstance(item_image, Item_Image)
        self.assertEqual(item_image.Item, self.item)
        self.assertEqual(item_image.Image, image)
        self.assertEqual(item_image.View_Detail, detail)
        self.assertEqual(item_image.Index, index)

class AdminDeleteItemTest(TestCase):
    def setUp(self):
        # Create admin user and log in
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        self.client = Client()
        self.client.login(username='admin', password='adminpass')

        # Create author and item
        self.author = Author.objects.create(Last_Name="Doe", First_Name="John")
        self.test_file = SimpleUploadedFile(
            name='test_delete.jpg',
            content=b'testcontent',
            content_type='image/jpeg'
        )
        self.item = Item.objects.create(
            Title="Delete Test Item",
            Miniature_Image=self.test_file,
            Upload_Date="2024-05-05",
            Media=1,
            Uploader=self.admin_user
        )
        self.item.Author.add(self.author)
        self.item.save()

    def test_non_admin_cannot_delete_item(self):
        # Log in as a non-admin user
        user = User.objects.create_user(username='user', password='userpass')
        self.client.logout()
        self.client.login(username='user', password='userpass')

        url = reverse('homepage:admin_delete_item', args=[self.item.pk])
        response = self.client.post(url)
        # Should be forbidden or redirected (403 or 302 to login)
        self.assertIn(response.status_code, [302, 403])
        # Item should still exist
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

    def test_admin_can_delete_item(self):
        # Confirm item exists
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

        # Call the admin_delete_item view
        url = reverse('homepage:admin_delete_item', args=[self.item.pk])
        response = self.client.post(url)

        # Should redirect after deletion
        self.assertEqual(response.status_code, 302)
        # Item should be deleted
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())
class ApproveRejectReturnItemTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        self.user = User.objects.create_user(username='user', password='userpass', email='user@example.com')
        self.client = Client()
        self.client.login(username='admin', password='adminpass')
        self.author = Author.objects.create(Last_Name="Doe", First_Name="John")
        self.item = Item.objects.create(
            Title="Pending Item",
            Miniature_Image=SimpleUploadedFile(name='pending.jpg', content=b'img', content_type='image/jpeg'),
            Upload_Date="2024-05-05",
            Media=1,
            Uploader=self.user,
            approve_status=0
        )
        self.item.Author.add(self.author)
        self.item.save()

    def test_approve_item(self):
        url = reverse('homepage:approve_item', args=[self.item.pk])
        response = self.client.post(url)
        self.item.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item.approve_status, 1)

    def test_reject_item(self):
        url = reverse('homepage:reject_item', args=[self.item.pk])
        response = self.client.post(url, {'reject_reason': 'Not good'})
        self.item.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item.approve_status, 2)

    def test_return_item_with_file(self):
        url = reverse('homepage:return_item', args=[self.item.pk])
        approval_file = SimpleUploadedFile(name='approval_file.pdf', content=b'pdfcontent', content_type='application/pdf')
        response = self.client.post(url, {'comment': 'Please fix', 'approval_file': approval_file})
        self.assertEqual(response.status_code, 302)
        record = Approve_Record.objects.filter(Item=self.item, Approval_Status=3).first()
        self.assertIsNotNone(record)
        self.assertTrue(record.Approval_File.name.startswith('approval_files/approval_file_'))
        self.assertTrue(record.Approval_File.name.endswith('.pdf'))

class EditItemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='userpass')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        assert self.client.login(username='user', password='userpass')
        self.author = Author.objects.create(Last_Name="Doe", First_Name="John")
        self.item = Item.objects.create(
            Title="Editable Item",
            Miniature_Image=SimpleUploadedFile(name='edit.jpg', content=b'img', content_type='image/jpeg'),
            Upload_Date="2024-05-05",
            Media=1,
            Uploader=self.user,
            approve_status=1
        )
        self.item.Author.add(self.author)
        self.item.save()
    def test_edit_item_get(self):
        url = reverse('homepage:item_edit', args=[self.item.pk])
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editable Item")

    def test_edit_item_post(self):
        url = reverse('homepage:item_edit', args=[self.item.pk])
        data = {
            'Title': 'Edited Title',
            'Upload_Date': '2024-05-06',
            'Media': 1,
            'Description': 'Updated description',
            'Alternate_Title': 'Alt Title',
            'Tags': 'tag1,tag2',
            'Language': 'en',
            'Provenance': 'Provenance',
            'Current_Collection_Location': 'Location',
            'Dimensions': '10x10',
            'Accession_Number': '123',
            'Bibliography': 'Some bibliography',
            'Author': 'John Doe',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [200, 302])
        self.item.refresh_from_db()
        self.assertEqual(self.item.Title, 'Edited Title')
        self.assertEqual(self.item.Description, 'Updated description')


class UserRegistrationLoginProfileTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register(self):
        url = reverse('homepage:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registration Pending Review')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_logout(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        url = reverse('homepage:user_login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)
        url = reverse('homepage:user_logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_user_profile(self):
        user = User.objects.create_user(username='profileuser', password='testpass')
        self.client.login(username='profileuser', password='testpass')
        url = reverse('homepage:user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profileuser')

class UserPermissionUpdateTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        self.user = User.objects.create_user(username='user', password='userpass')
        self.client = Client()
        self.client.login(username='admin', password='adminpass')

    def test_update_user_permission(self):
        url = reverse('homepage:update_user_permission')
        response = self.client.post(url, {'user_id': self.user.id, 'permission': 'is_staff', 'has_permission': 'true'})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.is_staff)