from test.support import EnvironmentVarGuard
import unittest
from unittest.mock import Mock, patch

from src.common.jwt_validator import Groups, JwtValidator
from tests.data import MOCK_Custom_authorizer


class TestJwtValidator(unittest.TestCase):

    @patch('src.common.jwt_validator.jwt')
    def test_jwt_validator_return_valid_user_group(self, mock_jwt):
        # given
        mock_jwt.get_unverified_claims = Mock(return_value={'cognito:groups': []})

        mock_token = MOCK_Custom_authorizer['authorizationToken']
        mock_event = {'headers': {'Authorization': mock_token}}

        # when
        response = JwtValidator.get_user_group_from_id_token(mock_event)

        # then
        self.assertEqual(response, [])

    @patch('src.common.jwt_validator.jwt')
    def test_jwt_validator_return_valid_user_id(self, mock_jwt):
        # given
        mock_jwt.get_unverified_claims = Mock(return_value={'sub': 'user sub'})

        mock_token = MOCK_Custom_authorizer['authorizationToken']
        mock_event = {'headers': {'Authorization': mock_token}}

        # when
        response = JwtValidator.get_user_id(mock_event)

        # then
        self.assertEqual(response, 'user sub')

    @patch('src.common.jwt_validator.jwt')
    def test_jwt_validator_return_valid_access(self, mock_jwt):
        # given
        mock_jwt.get_unverified_claims = Mock(return_value={'cognito:groups': ['admin']})

        mock_token = MOCK_Custom_authorizer['authorizationToken']
        mock_event = {'headers': {'Authorization': mock_token}}

        # when
        response = JwtValidator.is_have_an_access(event=mock_event, group=Groups.ADMIN)

        # then
        self.assertTrue(response)

        # given
        mock_jwt.get_unverified_claims = Mock(return_value={})

        # when
        response = JwtValidator.is_have_an_access(event=mock_event, group=Groups.ADMIN)

        # then
        self.assertFalse(response)

    def test_jwt_validator_raise_exception(self):
        with self.assertRaises(ValueError) as context:
            JwtValidator.is_have_an_access(event={}, group='')

        self.assertTrue('Group should be instance of Groups enum' in str(context.exception))


class TestJwtValidatorForOffline(unittest.TestCase):

    def test_jwt_validator_with_offline(self):
        # given
        env = EnvironmentVarGuard()
        with env:
            env.set('IS_OFFLINE', 'any value')

            mock_token = MOCK_Custom_authorizer['authorizationToken']
            mock_event = {'headers': {'Authorization': mock_token}}

            # when
            response = JwtValidator.get_user_group_from_id_token(mock_event)

            # then
            self.assertEqual(response, [None])

            # given
            env.set('LOCAL_USER_GROUP', 'any group')

            # when
            response = JwtValidator.get_user_group_from_id_token(mock_event)

            # then
            self.assertEqual(response, ['any group'])
