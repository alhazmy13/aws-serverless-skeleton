import json
import unittest
from unittest.mock import MagicMock

from src.app.post.model import PostModel
from src.common.encoder import ElasticSearchEncoder, PynamoDbEncoder


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


class TestElasticSearchEncoder(unittest.TestCase):
    def test_post_model_response(self):
        # given
        mock_model = MagicMock(spec=ElasticSearchEncoder)
        mock_model.title = "title"
        mock_model._l_ = {}

        # when
        encoder = ElasticSearchEncoder()
        result = encoder.default(mock_model)

        # then
        self.assertEqual(result, mock_model._l_)
