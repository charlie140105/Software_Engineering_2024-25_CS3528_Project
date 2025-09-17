import os
import django
from django.contrib.auth.models import User
from django.test import Client
from django.test.runner import DiscoverRunner
from django.core.management import call_command
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoBackend.settings'  # Replace with your project's settings module
django.setup()

# Global variable to store database state during tests
test_runner = DiscoverRunner()
old_database_config = None


def before_all(context):
    """
    Executed before all tests. Sets up the Django environment and creates the test database.
    """
    global old_database_config
    # Set up the test environment
    context.test_runner = test_runner
    # Setup code to run before all tests
    context.browser = webdriver.Chrome()
    # Create the test database
    old_database_config = context.test_runner.setup_databases()

    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument('--v=1')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    context.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    context.base_url = 'https://127.0.0.1'


def after_all(context):
    """
    Executed after all tests. Destroys the test database.
    """
    # Destroy the test database
    context.test_runner.teardown_databases(old_database_config)
    # Cleanup code to run after all tests
    context.browser.quit()


def before_scenario(context, scenario):
    """
    Executed before each scenario. You can do some initialization work here.
    """
    # Initialize global variables or set up preconditions here
    pass


def after_scenario(context, scenario):
    """
    Executed after each scenario. You can do some cleanup work here.
    """
    # Perform cleanup work here, such as resetting global variables
    pass
