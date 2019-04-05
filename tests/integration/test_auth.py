import copy
import unittest

from src.app.auth.authorizer import AuthorizerService
from src.app.auth.model import UserModel
from src.app.auth.post import PostAuthService
from tests.data import (MOCK_COGNITO_POST_EVENT, MOCK_Custom_authorizer)


class PostServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.event = MOCK_COGNITO_POST_EVENT
        self.user_sub = '9929942b-a90b-443d-96bf-19393615f6d7'

    def test_post_service_should_create_new_row_for_user(self):
        PostAuthService(event=self.event).execute()
        user = UserModel.get(self.user_sub)
        self.assertIsNotNone(user)

    def test_post_service_should_not_throw_exception_with_none_values(self):
        event = copy.deepcopy(self.event)
        event['userName'] = None
        response = PostAuthService(event=event).execute()
        self.assertIsNotNone(response)

    def test_post_service_should_update_current_user_if_it_exist(self):
        event = copy.deepcopy(self.event)
        PostAuthService(event=self.event).execute()
        event['request']['userAttributes']['given_name'] = 'foo'
        PostAuthService(event=event).execute()
        user = UserModel.get(self.user_sub)
        self.assertEqual(user.given_name, 'foo')


class AuthorizerServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.event = MOCK_Custom_authorizer

    def test_authorizer_service_should_throw_401_when_the_token_is_invalid(self):
        event = copy.deepcopy(self.event)
        event['authorizationToken'] = 'ANY_FAKE_TOKEN'
        auth_service = AuthorizerService(event=event)
        self.assertRaises(Exception,
                          auth_service.execute)

    def test_authorizer_service_should_throw_401_when_the_token_is_empty(self):
        event = copy.deepcopy(self.event)
        event['authorizationToken'] = ''

        auth_service = AuthorizerService(event=event)
        self.assertRaises(Exception,
                          auth_service.execute)

    def test_authorizer_service_should_return_valid_policy(self):
        event = copy.deepcopy(self.event)
        auth_response = AuthorizerService(event=event).execute()
        resource = auth_response['policyDocument']['Statement'][0]['Resource'][0].split('/')
        self.assertEqual(auth_response['policyDocument']['Statement'][0]['Effect'],
                         'Allow')
        self.assertEqual(resource[2], '*')
        self.assertEqual(resource[3], '*')
        self.assertEqual(auth_response['policyDocument']['Statement'][0]['Action'],
                         'execute-api:Invoke')
        self.assertEqual(auth_response['principalId'], "9929942b-a90b-443d-96bf-19393615f6d7")
