import unittest
from unittest.mock import MagicMock, patch

from src.app.upload.create import CreatePreSignedUrlService
from src.app.upload.model import AssetModel
from tests.src.app.upload import aws_mock


class TestCreateService(unittest.TestCase):
    @patch('src.app.upload.create.AssetModel')
    @patch('src.app.upload.create.boto3')
    def test_create_service_return_presigend_url(self, mock_boto3, mock_upload_model):
        # given
        mock_boto3.client = aws_mock.client
        conn = mock_boto3.client('s3')
        conn.create_bucket(Bucket='my-bucket')

        upload_obj = AssetModel()
        mock_upload = MagicMock(spec=upload_obj)
        mock_upload.id = "random id"

        mock_upload_model.create = MagicMock(return_value=mock_upload)

        # when
        service = CreatePreSignedUrlService("user sub")
        response = service.execute.__wrapped__(service)

        # then
        mock_upload.save.assert_called_once()
        self.assertEqual(response, {"upload_url": "random url",
                                    "id": "random id"})
