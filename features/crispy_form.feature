Feature: Test Crispy Form in Django

  Scenario: Valid form submission
    Given I have a valid form data
    When I submit the form
    Then the form should be valid

  Scenario: Invalid form submission
    Given I have an invalid form data
    When I submit the form
    Then the form should be invalid
