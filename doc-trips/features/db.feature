Feature: database access restriction

  Scenario: access database page without logging in
    Given any starting point
    When I visit database with a live browser
    Then I should be redirected to the Dartmouth login page

  Scenario: access database page as a regular logged in  user
    Given a user
    And the user is logged in
    When I get "/db/2014/"
    Then I should see a "403" error

  Scenario: access database page as a director
    Given a user
    And the user is a director
    And the user is logged in
    When I get "/db/2014/"
    Then the result page should include "Database Index"

  Scenario: access permission portal as a user    
    Given a user 
    And the user is logged in
    When I get "/permissions/set/"
    Then I should see a "403" error

  Scenario: access permission portal director
    Given a user
    And the user is a director
    And the user is logged in
    When I get "/permissions/set/"
    Then the result page should include "permission"
    
  
