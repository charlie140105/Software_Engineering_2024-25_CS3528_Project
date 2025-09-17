Feature: Test Review function in Django

  Scenario: Approve item review
    Given I am admin and on the review item tab
    When I approve the first item
    Then the first item should be approve

  Scenario: Reject user review
    Given I am admin and on the review user tab
    When I reject the second item
    Then the second user should be reject