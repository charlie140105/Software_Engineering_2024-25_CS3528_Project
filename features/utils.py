from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.contrib.auth.models import User


def create_and_login_admin(context, username='admin', password='adminpassword', email='admin@example.com'):
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)

    # Open the login page
    context.browser.get(context.base_url + '/login')

    # Wait for the login form to be present
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(username)
    context.browser.find_element(By.NAME, "password").send_keys(password)

    try:
        submit_button = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        submit_button.click()
    except TimeoutException as e:
        print("Waiting for element to be clickable timed out: ", e)
        context.browser.save_screenshot("debug_screenshot.png")  # Save a screenshot for debugging
