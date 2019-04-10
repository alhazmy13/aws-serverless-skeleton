from src.common.log import get_logger


class ExceptionHandler(object):
    @classmethod
    def handel_exception(cls, exception):
        get_logger().warning(exception, exc_info=True)


class UnAuthorizedException(Exception):
    """User does not have an access to this resource"""


class UnAuthorizedUpdateResourceException(Exception):
    """ User does not have an access to update the resource """


class NoContentAvailableException(Exception):
    """System does not have a content for this resource"""


class ESException(Exception):
    """Exception capturing status_code from Client Request"""
    status_code = 0
    payload = ''

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        Exception.__init__(self,
                           'ES_Exception: status_code={}, payload={}'.format(status_code, payload))


class DataMissingException(Exception):
    """will be used when System receive unexpected count of data from Client"""


class ValidationException(Exception):
    """Request body invalid."""


class InvalidKeyException(Exception):
    """Invalid path parameter for post."""


class ItemNotFoundException(Exception):
    """ Exception when the item is not found or
    when the user doesnt have an access to requested item"""


class S3UnsupportedEvent(Exception):
    """Exception when the trigger called with Unsupported event name"""
