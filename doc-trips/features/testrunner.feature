
Feature: The testrunner in environment.py works

  Scenario: run a feature
    Given a user
   
  Scenario: run another feature
    Given any starting point
    When I try and get user out of the database
    Then I should not find the user

  Scenario: any feature
    Given any starting point
    When I use the browser
    And I use the client
    And I use test.assert
    Then they all work






