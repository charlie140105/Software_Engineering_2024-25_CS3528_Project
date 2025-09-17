from behave import given, when, then
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver


@given('I am on the registration page')
def step_impl(context):

    context.browser.get(context.base_url + '/register')


@when('I fill out the registration form with valid data')
def step_impl(context):
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.NAME, 'first_name'))
    ).send_keys('John')
    context.browser.find_element(By.NAME, 'last_name').send_keys('Doe')
    context.browser.find_element(By.NAME, 'email').send_keys('john.doe@example.com')
    context.browser.find_element(By.NAME, 'username').send_keys('john_doe')
    context.browser.find_element(By.NAME, 'password1').send_keys('securepassword123')
    context.browser.find_element(By.NAME, 'password2').send_keys('securepassword123')


@when('I submit the registration form')
def step_impl(context):
    try:
        submit_button = WebDriverWait(context.browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Register')]"))
        )
        submit_button.click()
    except TimeoutException as e:
        print("Waiting for element to be clickable timed out: ", e)
        context.browser.save_screenshot("debug_screenshot.png")


@then('I should see a message indicating that my registration is pending approval')
def step_impl(context):
    try:
        message = WebDriverWait(context.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'container'))
        )
        assert 'Pending' in message.text
    except TimeoutException:
        context.browser.save_screenshot('timeout_exception.png')
        raise
