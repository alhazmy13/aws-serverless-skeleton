import unittest
from unittest.mock import MagicMock

from src.app.post.model import PostModel
from src.common.encoder import PynamoDbEncoder


class TestPynamoDbEncoder(unittest.TestCase):
    def test_post_model_response(self):
        # given
        mock_model = MagicMock(spec=PostModel)
        mock_model.title = "title"
        mock_model.attribute_values = {}

        # when
        encoder = PynamoDbEncoder()
        result = encoder.default(mock_model)

        # then
        self.assertEqual(result, mock_model.attribute_values)
