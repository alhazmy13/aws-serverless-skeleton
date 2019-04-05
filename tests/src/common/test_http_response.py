from http import HTTPStatus
import unittest

from src.common.http_response import HTTPResponse


class TestHTTPResponse(unittest.TestCase):
    def test_to_json_response_without_message(self):
        # given
        response_code = HTTPStatus.OK

        # when
        response = HTTPResponse.to_json_response(response_code)

        # then
        self.assertEqual(response.get('statusCode'), response_code.value)
        self.assertEqual(response.get('body'),
                         "{\"message\": \"" + response_code.description + "\"}")

    def test_to_json_response_with_message(self):
        # given
        response_code = HTTPStatus.BAD_REQUEST
        response_message = "dummy"

        # when
        response = HTTPResponse.to_json_response(response_code, response_message)

        # then
        self.assertEqual(response.get('statusCode'), response_code.value)
        self.assertEqual(response.get('body'),
                         "{\"message\": \"" + response_message + "\"}")
