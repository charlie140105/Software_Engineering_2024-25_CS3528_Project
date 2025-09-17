from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from behave import given, when, then

@given('I am on the home page')
def step_impl(context):
    context.browser.get(context.base_url + '/')

@when('I visit the help page')
def step_impl(context):
    try:
        help_link = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Help"))
        )
        help_link.click()
    except TimeoutException as e:
        print("Waiting for element to be clickable timed out: ", e)
        context.browser.save_screenshot("debug_screenshot.png")  # Save screenshot for debugging

@then('I should see "How to Use Our Website"')
def step_impl(context):
    try:
        # Wait for the header to be present
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "header"))
        )
        # Find the <h1> element within the header
        header_h1 = context.browser.find_element(By.CSS_SELECTOR, "header h1")
        assert header_h1.text == "How to Use Our Website", f"Expected 'How to Use Our Website', but found '{header_h1.text}'"
        WebDriverWait(context.browser, 5).until(lambda driver: False)
    except TimeoutException as e:
        print("Header or <h1> element not found: ", e)
        context.browser.save_screenshot("debug_screenshot.png")  # Save screenshot for debugging
        assert False, "The header or <h1> element was not found on the page."