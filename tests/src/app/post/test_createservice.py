import json
import unittest
from unittest.mock import MagicMock, patch

from src.app.post.create import CreateService
from tests.data import MOCK_POST_REQUEST


class TestCreateService(unittest.TestCase):
    @patch('src.app.post.create.PostModel')
    @patch('src.app.post.create.ExceptionHandler')
    def test_create_success(self, mock_exception_handler, mock_post_model):
        # given
        mock_post = MagicMock()

        mock_post_model.create = MagicMock(return_value=mock_post)

        # when
        body = json.dumps(MOCK_POST_REQUEST)
        service = CreateService(body, "user sub")
        response = service.execute.__wrapped__(service)
        # then
        # mock_post_model.query.assert_called_with("user sub")
        mock_post_model.create.assert_called_with(user_sub="user sub", data=MOCK_POST_REQUEST)
        mock_post.save.assert_called_once()
        mock_exception_handler.handel_exception.assert_not_called()
        self.assertEqual(response, mock_post)
