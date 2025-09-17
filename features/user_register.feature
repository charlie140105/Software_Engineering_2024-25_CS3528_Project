# Created by luo at 2024/7/16
Feature: User Registration
  As a new user
  I want to be able to register using a registration form
  So that I can access user-specific features after my account is approved

  Scenario: Successful Registration
    Given I am on the registration page
    When I fill out the registration form with valid data
    And I submit the registration form
    Then I should see a message indicating that my registration is pending approval
