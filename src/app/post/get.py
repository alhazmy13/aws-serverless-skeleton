from http import HTTPStatus

from src.app.post.enum import PostStatus
from src.app.post.model import PostModel
from src.common.authorization import Authorizer
from src.common.decorator import api_response
from src.common.exceptions import (ExceptionHandler, ItemNotFoundException)


class GetService(object):
    def __init__(self, path_param, user_group):
        self.path_param = path_param
        self.user_group = user_group

    @api_response()
    def execute(self):
        try:
            if Authorizer.is_admin(user_group=self.user_group):
                return self._get_post_object()
            return self._find_filtered_result()
        except ItemNotFoundException as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.NOT_FOUND
        except PostModel.DoesNotExist as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.NOT_FOUND

    def _get_post_object(self, query_filter=None):
        for item in PostModel.query(self.path_param, query_filter):
            return item
        raise ItemNotFoundException

    def _find_filtered_result(self):
        return self._get_post_object(
            query_filter=PostModel.status.is_in(PostStatus.PUBLISHED.value))
