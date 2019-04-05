from functools import wraps
import os

import src.common.context
from src.common.encoder import PynamoDbEncoder
from src.common.http_response import HTTPResponse, HTTPStatus
from src.common.log import get_logger


def api_response(encoder=PynamoDbEncoder):
    def _response(view_func):
        def _decorator(request, *args, **kwargs):
            res = view_func(request, *args, **kwargs)
            if type(res) is tuple and len(res) == 2:
                return HTTPResponse.to_json_response(res[0], res[1])
            else:
                if isinstance(res, HTTPStatus):
                    return HTTPResponse.to_json_response(res)
                return HTTPResponse.to_ok_json(body=res, encoder=encoder)

        return wraps(view_func)(_decorator)

    return _response


def gateway_request_interceptor(lambda_func):
    @wraps(lambda_func)
    def _wrapper(event, context):
        if event and 'requestContext' in event:
            request_context = event.get('requestContext')
            if 'requestId' in request_context:
                src.common.context.REQUEST_ID = request_context.get('requestId')
            if os.environ.get('STAGE') is not 'prod' and 'authorizer' in request_context:
                get_logger().debug("Lambda event: %s", request_context.get('authorizer'))

        try:
            return lambda_func(event, context)
        except Exception:
            get_logger().error("Error within lambda function.", exc_info=1)
            raise

    return _wrapper
