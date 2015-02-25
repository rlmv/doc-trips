
from behave import *
from django.contrib.auth import get_user_model

@when('I try and get user out of the database')
def step_get_user(context):
    context.users = get_user_model().objects.all()
    
@then('I should not find the user')
def step_not_found(context):
    context.test.assertEquals(len(context.users), 0)

@when('I use the browser')
def step_use_browser(context):
    context.browser.visit('/')

@when('I use the client')
def step_use_client(context):
    context.response = context.client.get('/')

@when('I use test.assert')
def step_assert(context):
    context.test.assertEquals(True, not False)

@then('they all work')
def step_impl(context):
    context.test.assertEquals(context.response.status_code, 200)
    context.browser.ensure_success_response()
