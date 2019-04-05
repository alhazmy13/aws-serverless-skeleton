import unittest
from unittest.mock import call, MagicMock, patch


import src.common.context
from src.common.decorator import api_response
from src.common.decorator import gateway_request_interceptor
from src.common.encoder import PynamoDbEncoder
from src.common.http_response import HTTPStatus


class TestDecorator(unittest.TestCase):
    @patch('src.common.decorator.get_logger')
    @patch('os.environ')
    def test_gateway_request_interceptor_request_id_present(self, mock_environ, mock_logger):
        # given
        context = {}
        authorizer = {}
        event = {'requestContext': {'requestId': '12345', 'authorizer': authorizer}}
        mock_environ.get = MagicMock(return_value="dev")

        mock_method = MagicMock()

        # when
        decorated = gateway_request_interceptor(mock_method)
        result = decorated(event=event, context=context)

        # then
        self.assertEqual(src.common.context.REQUEST_ID, '12345')
        self.assertEqual(result, mock_method.return_value)
        mock_method.assert_called_with(event, context)
        self.assertEqual(mock_logger.return_value.debug.mock_calls, [
            call("Lambda event: %s", {})])

    @patch('src.common.decorator.get_logger')
    @patch('os.environ')
    def test_gateway_request_interceptor_request_id_present_prod(self, mock_environ, mock_logger):
        # given
        context = {}
        authorizer = {}
        event = {'requestContext': {'requestId': '12345', 'authorizer': authorizer}}
        mock_environ.get = MagicMock(return_value="prod")

        mock_method = MagicMock()

        # when
        decorated = gateway_request_interceptor(mock_method)
        result = decorated(event=event, context=context)

        # then
        self.assertEqual(src.common.context.REQUEST_ID, '12345')
        self.assertEqual(result, mock_method.return_value)
        mock_method.assert_called_with(event, context)
        mock_logger.return_value.debug.assert_not_called()

    @patch('src.common.decorator.get_logger')
    @patch('os.environ')
    def test_gateway_request_interceptor_request_id_not_present(self, mock_environ, mock_logger):
        # given
        event = {'application': 'my app'}
        context = {'dummy': 1}
        mock_environ.get = MagicMock(return_value="dev")
        src.common.context.REQUEST_ID = None

        mock_method = MagicMock()

        # when
        decorated = gateway_request_interceptor(mock_method)
        result = decorated(event=event, context=context)

        # then
        self.assertEqual(src.common.context.REQUEST_ID, None)
        self.assertEqual(result, mock_method.return_value)
        mock_method.assert_called_with(event, context)
        mock_logger.return_value.debug.assert_not_called()

    @patch('src.common.decorator.get_logger')
    @patch('os.environ')
    def test_gateway_request_interceptor_lambda_exception(self, mock_environ, mock_logger):
        # given
        event = {'application': 'my app'}
        context = {'dummy': 1}
        mock_environ.get = MagicMock(return_value="dev")
        src.common.context.REQUEST_ID = None

        mock_exception = Exception()
        mock_method = MagicMock(side_effect=[mock_exception])

        # when
        decorated = gateway_request_interceptor(mock_method)

        # then
        try:
            decorated(event=event, context=context)
        except Exception as ex:
            self.assertEqual(ex, mock_exception)

        self.assertEqual(src.common.context.REQUEST_ID, None)
        mock_method.assert_called_with(event, context)
        mock_logger.return_value.debug.assert_not_called()
        self.assertEqual(mock_logger.return_value.error.mock_calls, [
            call("Error within lambda function.", exc_info=1)])

    @patch('src.common.decorator.HTTPResponse')
    def test_api_response_with_status_only(self, mock_http_response):
        # given
        mock_method = MagicMock(return_value=HTTPStatus.BAD_REQUEST)

        # when
        decorator = api_response()
        decorated = decorator(mock_method)
        decorated("dummy")

        # then
        self.assertEqual(mock_http_response.to_json_response.call_args,
                         call(HTTPStatus.BAD_REQUEST))
        self.assertEqual(mock_method.call_args, call("dummy"))

    @patch('src.common.decorator.HTTPResponse')
    def test_api_response_without_status(self, mock_http_response):
        # given
        mock_method = MagicMock(return_value="response")

        # when
        decorator = api_response()
        decorated = decorator(mock_method)
        decorated("dummy")

        # then
        self.assertEqual(mock_http_response.to_ok_json.call_args,
                         call(body="response", encoder=PynamoDbEncoder))
        self.assertEqual(mock_method.call_args, call("dummy"))

    @patch('src.common.decorator.HTTPResponse')
    def test_api_response_with_both_response_and_status(self, mock_http_response):
        # given
        mock_method = MagicMock(return_value=(HTTPStatus.BAD_REQUEST, "response"))

        # when
        decorator = api_response()
        decorated = decorator(mock_method)
        decorated("dummy")

        # then
        self.assertEqual(mock_http_response.to_json_response.call_args,
                         call(HTTPStatus.BAD_REQUEST, "response"))
        self.assertEqual(mock_method.call_args, call("dummy"))
