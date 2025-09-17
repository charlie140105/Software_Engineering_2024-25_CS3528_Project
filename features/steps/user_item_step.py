from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from features.utils import create_and_login_admin
from behave import given, when, then

@given("I'm logged in as administrator")
def step_impl(context):
    create_and_login_admin(context)

@when('I click Myitem')
def step_impl(context):
    try:
        my_item_link = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "My Items"))  # Use link text to find the element
        )
        my_item_link.click()
    except TimeoutException as e:
        print("Waiting for element to be clickable timed out: ", e)
        context.browser.save_screenshot("debug_screenshot.png")  # Save screenshot for debugging


@then('I should see MyItem page')
def step_impl(context):
    try:
        edit_item_element = WebDriverWait(context.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "home-content-container"))  # Ensure the ID is correct
        )
        assert edit_item_element is not None
        WebDriverWait(context.browser, 10).until(lambda driver: False)
    except TimeoutException as e:
        print("Waiting for Edit item element timed out: ", e)
        context.browser.save_screenshot("debug_screenshot_edit_item.png")  # Save screenshot for debugging


