from functools import wraps

from src.app.post.enum import PostStatus
from src.common.exceptions import ValidationException


def validate_post_request(method):
    @wraps(method)
    def _wrapper(cls, user_sub, data):
        try:
            if data.get('status') not in PostStatus.list():
                raise ValidationException
        except Exception as ex:
            raise ValidationException(ex)
        return method(cls, user_sub, data)

    return _wrapper
