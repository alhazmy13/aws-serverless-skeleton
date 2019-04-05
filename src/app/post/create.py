from http import HTTPStatus
import json

from src.app.post.model import PostModel
from src.common.decorator import api_response
from src.common.exceptions import (ExceptionHandler,
                                   ValidationException)


class CreateService(object):
    """ Service to create new post object and save it in DynamoDB """

    def __init__(self, body, user_sub):
        """
        :param body: dict
        :param user_sub: user is as string
        :return: http response
        """
        self.body = body
        self.user_sub = user_sub

    @api_response()
    def execute(self):
        """
        execute function
        :return: http response
        """
        try:
            post_object = self.create_post_object()
            post_object.save()
            return post_object
        except ValidationException as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST, str(ex)

    def create_post_object(self):
        """
         function to create new Post object
         :return: http response
         """
        return PostModel.create(user_sub=self.user_sub,
                                data=json.loads(self.body))
