
from behave import *
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

@given('a user')
def step_user(context):
    context.username = 'user'
    context.password = 'password'
    context.user = get_user_model().objects.create_user(username=context.username, password=context.password)

@given('the user is logged in')
def step_log_in(context):
    context.client.login(username=context.username, password=context.password)

@when('the user gets "{url_name}"')
def step_get_url(context, url_name):

    context.response = context.client.get(reverse(url_name))
    
@then('the user should get a "{status_code:d}" error')
def step_impl(context, status_code):

    context.test.assertEquals(context.response.status_code, 403)
   


