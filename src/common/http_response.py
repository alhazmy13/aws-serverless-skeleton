from http import HTTPStatus
import json

from src.common.encoder import PynamoDbEncoder


class HTTPResponse(object):
    @classmethod
    def to_json_response(cls, http_status, message=None):
        """
        Access-Control-Allow-Origin is needed for CORS to work
        Access-Control-Allow-Credentials is needed for cookies
        """
        _message = http_status.description
        if message:
            _message = message
        return {
            "statusCode": http_status.value,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps({"message": _message})}

    @classmethod
    def to_ok_json(cls, body, encoder=PynamoDbEncoder):
        return {
            "statusCode": HTTPStatus.OK.value,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps(body, cls=encoder)
        }
