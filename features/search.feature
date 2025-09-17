Feature: Test Search Form in Django

  Scenario: Input Search Date
    Given I input a title search data
    When I click the search button
    Then the search form should display the result

