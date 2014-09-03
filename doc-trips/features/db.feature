Feature: database access restriction

  Scenario: access database page as a regular user
    Given a user
    And the user is logged in
    When the user gets "db:index""
    Then the user should get a "403" error

    
  