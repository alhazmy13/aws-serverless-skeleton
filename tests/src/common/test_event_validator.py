import unittest

from src.common.event_validator import EventValidator


class TestEventValidator(unittest.TestCase):
    def test_get_query_validator(self):
        # given
        mock_dict_request = dict(queryStringParameters={'id': 'value'})

        # when
        validator = EventValidator()
        result = validator.get_query_from_event(event=mock_dict_request, key='id')

        # then
        self.assertEqual(result, 'value')

        # when
        mock_dict_request.pop('queryStringParameters')
        result = validator.get_query_from_event(event=mock_dict_request, key='id')

        # then
        self.assertIsNone(result)

    def test_path_parm_validator(self):
        # given
        mock_dict_request = dict(pathParameters={'id': 'value'})

        # when
        validator = EventValidator()
        result = validator.get_path_parameters_from_event(event=mock_dict_request, key='id')

        # then
        self.assertEqual(result, 'value')

        # when
        mock_dict_request.pop('pathParameters')
        result = validator.get_query_from_event(event=mock_dict_request, key='id')

        # then
        self.assertIsNone(result)

    def test_user_sub_validator(self):
        # given
        mock_dict_request = dict(requestContext={'authorizer': {'claims': {'sub': 'SUB'}}})

        # when
        validator = EventValidator()
        result = validator.get_user_sub_from_event(event=mock_dict_request)

        # then
        self.assertEqual(result, 'SUB')

        # when
        mock_dict_request = dict(requestContext={'authorizer': {'principalId': 'SUB'}})
        result = validator.get_user_sub_from_event(event=mock_dict_request)

        # then
        self.assertEqual(result, 'SUB')
