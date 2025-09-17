Feature: Test Edit function in Django

  Scenario: Edit item
    Given I am uploader and on edit page
    And I modify the text information
    And Add new image
    When I save changes
    Then the item should be edit sucessfully

