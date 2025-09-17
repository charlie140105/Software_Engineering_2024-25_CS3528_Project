from behave import given, when, then
from django.test import Client
from django.urls import reverse
from homepage.forms import ItemInfoForm
from datetime import datetime
import pytz
from django.core.files.uploadedfile import SimpleUploadedFile

client = Client()


@given('I have a valid form data')
def step_given_valid_form_data(context):
    # Create a virtual image file
    image_file = SimpleUploadedFile(
        name='test_image.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )

    context.form_data = {
        'Title': 'Sample Project',
        'Upload_Images': [image_file],
        'Author': 'John Doe',
        'Upload_Date': datetime.now(pytz.UTC).strftime('%Y-%m-%d'),
        'IsRti': False,
        'Description': 'Sample description',
        'Alternate_Title': 'Alternate Title',
        'Language': 'en',
        'Provenance': 'Unknown',
        'Current_Collection_Location': 'Museum',
        'Dimensions': '10x10 cm',
        'Accession_Number': '12345',
        'Tags': 'sample, test',
        'Bibliography': 'Sample bibliography'
    }


@given('I have an invalid form data')
def step_given_invalid_form_data(context):
    context.form_data = {
        'Title': '',  # Title is required, leaving it blank should make the form invalid
        'Upload_Images': [],  # Assuming we are not testing file uploads here
        'Author': 'John Doe',
        'Upload_Date': datetime.now(pytz.UTC).strftime('%Y-%m-%d'),
        'IsRti': False,
        'Description': 'Sample description',
        'Alternate_Title': 'Alternate Title',
        'Language': 'en',
        'Provenance': 'Unknown',
        'Current_Collection_Location': 'Museum',
        'Dimensions': '10x10 cm',
        'Accession_Number': '12345',
        'Tags': 'sample, test',
        'Bibliography': 'Sample bibliography'
    }


@when('I submit the form')
def step_when_submit_form(context):
    context.response = client.post(reverse('homepage:upload_item'), data=context.form_data)


@then('the form should be valid')
def step_then_form_should_be_valid(context):
    form = ItemInfoForm(data=context.form_data)
    assert form.is_valid(), f"Form errors: {form.errors.as_data()}"


@then('the form should be invalid')
def step_then_form_should_be_invalid(context):
    form = ItemInfoForm(data=context.form_data)
    assert not form.is_valid(), "Form should be invalid but it is valid"
