from behave import given, when, then
from django.urls import reverse
from django.test import Client


@given('I have a working Django project')
def step_impl(context):
    context.client = Client()


@when('I visit the homepage')
def step_impl(context):
    context.response = context.client.get(reverse('homepage:home'))


@then('I should see "DHPA"')
def step_impl(context):
    assert "DHPA" in context.response.content.decode()
