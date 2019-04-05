import unittest
from unittest.mock import MagicMock, patch

from src.app.post.list import ListService


class TestListService(unittest.TestCase):
    @patch('src.app.post.list.PostModel')
    def test_list_success(self, mock_post_model):
        # given
        mock_post = MagicMock()

        mock_post_model.scan = MagicMock(return_value=[None, mock_post])

        # when
        service = ListService(offset=1, limit=1)
        response = service.execute.__wrapped__(service)

        # then
        self.assertEqual(response, [mock_post])
