from http import HTTPStatus
import unittest
from unittest.mock import MagicMock, patch

from src.app.post.get import GetService


class TestGetService(unittest.TestCase):

    @patch('src.app.post.get.ExceptionHandler')
    @patch('src.app.post.get.Authorizer')
    @patch('src.app.post.get.PostModel')
    def test_user_get_post(self, mock_post_model, mock_authorizer, mock_exception_handler):
        # given
        user_group = "my group"
        path_param = "path param"

        mock_post = MagicMock(spec=mock_post_model)
        mock_post.status = "PUBLISHED"

        mock_post_model.query = MagicMock(return_value=[mock_post])

        mock_authorizer.is_admin = MagicMock(return_value=False)

        # when
        service = GetService(path_param, user_group)
        response = service.execute.__wrapped__(service)

        # then
        mock_authorizer.is_admin.assert_called_with(user_group=user_group)

        mock_exception_handler.handel_exception.assert_not_called()
        self.assertEqual(response, mock_post)

    @patch('src.app.post.get.Authorizer')
    @patch('src.app.post.get.PostModel')
    def test_not_found(self, mock_post_model, mock_authorizer):
        # given
        user_group = "my group"
        path_param = "path param"

        mock_post = MagicMock(spec=mock_post_model)
        mock_post.status = "DRAFT"

        mock_post_model.query = MagicMock(return_value=[])
        mock_authorizer.is_admin = MagicMock(return_value=False)

        # when
        service = GetService(path_param, user_group)
        response = service.execute.__wrapped__(service)

        # then
        mock_authorizer.is_admin.assert_called_with(user_group=user_group)
        self.assertEqual(response, HTTPStatus.NOT_FOUND)

    @patch('src.app.post.get.ExceptionHandler')
    @patch('src.app.post.get.Authorizer')
    @patch('src.app.post.get.PostModel')
    def test_admin_gets_post(self, mock_post_model, mock_authorizer, mock_exception_handler):
        # given
        user_group = "user group"
        path_param = "path param"

        mock_post = MagicMock()

        mock_post_model.query = MagicMock(return_value=[mock_post])

        mock_authorizer.is_admin = MagicMock(return_value=True)

        # when
        service = GetService(path_param, user_group)
        response = service.execute.__wrapped__(service)

        # then
        mock_authorizer.is_admin.assert_called_with(user_group=user_group)
        mock_exception_handler.handel_exception.assert_not_called()
        self.assertEqual(response, mock_post)
