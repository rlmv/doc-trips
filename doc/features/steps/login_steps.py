
import splinter
from behave import *
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from doc.permissions import directors

@given('any starting point')
def step_nothing(context):
    pass

@given('a user')
def step_user(context):
    context.username = 'user'
    context.password = 'password'
    context.user = get_user_model().objects.create_user(username=context.username, password=context.password)

@given('the user is logged in')
def step_log_in(context):
    context.client.login(username=context.username, password=context.password)

@given('the user is a director')
def step_director(context):
    context.user.groups.add(directors())

@when('I get "{url}"')
def step_get_url(context, url):
    context.browser.visit(url)
    context.response = context.client.get(url)
    
@then('I should see a "{status_code:d}" error')
def step_impl(context, status_code):
    context.test.assertEquals(context.response.status_code, 403)

@then('the result page should include "{text}"')
def step_result_page(context, text):
    if text not in str(context.response.content):
        raise Exception('%r not in %r' % (text, context.response.content))

@when('I visit database with a live browser')
def step_live_browser(context):
    context.browser.visit(context.live_test_case.live_server_url + '/db/2014')

@then('I should be redirected to the Dartmouth login page')
def step_redirect_to_login(context):
    check = 'Dartmouth Web Authentication' in str(context.browser.html)
    context.test.assertEqual(check, True, 'not redirected to Dartmouth login %s' % context.browser.html)

    
