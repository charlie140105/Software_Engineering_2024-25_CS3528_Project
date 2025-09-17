from django.test import TestCase
from django.utils import timezone
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from homepage.forms import MultipleFileField, SearchForm, ItemInfoForm

class TestForms(TestCase):
    def setUp(self):
        self.field = MultipleFileField()

        self.search_form = SearchForm(data={
            'title': 'projectA',
            'author': 'David',
            'datefrom': '2024-01-20',
            'dateto': '',
            'files_Still_Images': True,
            'file_RTI': True,
        })

        self.item_info_form = ItemInfoForm(data={
            'Title': 'projectB',
            'isRti': False,
            'Upload_Images': 'test_img.jpg',
            'Author': 'Peter',
            'Upload_Date': timezone.now(),
            'Email': '123@abc.com'
        })

    def test_widget_type(self):
        self.assertIsInstance(self.field.widget, forms.ClearableFileInput)

    def test_widget_attrs(self):
        self.assertEqual(self.field.widget.attrs['id'], 'upload_images')
        self.assertTrue(self.field.widget.allow_multiple_selected)

    def test_clean_single_file(self):
        file_data = SimpleUploadedFile("file.jpg", b"file content")
        cleaned_data = self.field.clean(file_data)
        self.assertEqual(cleaned_data, file_data)

    def test_clean_multiple_files(self):
        file1 = SimpleUploadedFile("file1.jpg", b"file1 content")
        file2 = SimpleUploadedFile("file2.jpeg", b"file2 content")
        file3 = SimpleUploadedFile("file3.png", b"file3 content")
        file4 = SimpleUploadedFile("file4.tif", b"file4 content")
        file5 = SimpleUploadedFile("file5.jpeg2000", b"file5 content")
        cleaned_data = self.field.clean([file1, file2,file3,file4,file5])
        self.assertEqual(cleaned_data, [file1, file2,file3,file4,file5])

    def test_search_form_init(self):
        self.assertTrue(self.search_form.is_valid())

    def test_item_info_form_init(self):
        self.assertTrue(self.item_info_form.is_valid())