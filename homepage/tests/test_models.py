from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from homepage.models import Author, Item, Item_Image, RTI_File, Planes, Approve_Record


class TestModels(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            Last_Name="Doe",
            First_Name="John"
        )
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.item = Item.objects.create(
            Title='Image_Title',
            Upload_Date=timezone.now(),
            Miniature_Image=SimpleUploadedFile(name='test_img.jpg', content=b'', content_type='image/jpeg'),
            Media=1,
            Uploader=self.user
        )
        self.item.Author.add(self.author)

        self.item_image = Item_Image.objects.create(
            Item=self.item,
            Image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            View_Detail='Test View Detail',
            Index=1
        )
        self.rti_file = RTI_File.objects.create(
            PTM_File=SimpleUploadedFile(name='rti_file.ptm', content=b'', content_type='application/ptm'),
            Has_Image=True,
            Info_File=SimpleUploadedFile(name='info.xml', content=b'{}', content_type='application/xml'),
            Item=self.item
        )
        self.planes = Planes.objects.create(
            File=SimpleUploadedFile(name='plane_file.jpg', content=b'', content_type='image/jpeg'),
            RTI_File=self.rti_file
        )

    def test_author_name(self):
        author_name = self.author.Name
        self.assertEqual(author_name, "Doe John")

    def test_author_str(self):
        author_str = str(self.author)
        self.assertEqual(author_str, "John Doe")

    def test_item_str(self):
        item_str = str(self.item)
        self.assertEqual(item_str, "Item Image_Title")

    def test_item_image_str(self):
        item_image_str = str(self.item_image)
        self.assertIn("test_image", item_image_str)

    def test_plane_str(self):
        plane_str = str(self.planes)
        self.assertIn("plane_file", plane_str)

    def test_approve_record(self):
        approval_admin = User.objects.create_user(username='adminuser', password='12345')
        approve_record = Approve_Record.objects.create(
            Item=self.item,
            Approval_Admin=approval_admin,
            Approval_Status=1,
            Approval_File=SimpleUploadedFile(name='approval_file.pdf', content=b'', content_type='application/pdf'),
            Approval_Comment='Test comment'
        )
        self.assertEqual(str(approve_record), "Approval Item Image_Title")

    def test_approve_record_create_method(self):
        approval_admin = User.objects.create_user(username='adminuser', password='12345')
        approval_file = SimpleUploadedFile(name='approval_file.pdf', content=b'', content_type='application/pdf')
        new_approval = Approve_Record.create(
            item=self.item,
            admin=approval_admin,
            status=2,
            file=approval_file,
            comment='Test comment'
        )
        new_approval.save()
        self.assertEqual(new_approval.Item, self.item)
        self.assertEqual(new_approval.Approval_Admin, approval_admin)
        self.assertEqual(new_approval.Approval_Status, 2)
        self.assertIn('approval_file', new_approval.Approval_File.name,)
        self.assertEqual(new_approval.Approval_Comment, 'Test comment')
