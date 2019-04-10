from http import HTTPStatus
import unittest
from unittest.mock import MagicMock, patch

from src.app.upload.bucket import BucketTriggerService
from src.app.upload.model import AssetModel
from src.common.exceptions import S3UnsupportedEvent


class TestBucketService(unittest.TestCase):

    @patch('src.app.upload.bucket.AssetModel')
    @patch('src.app.upload.bucket.ExceptionHandler')
    def test_trigger_with_created_event(self, mock_exception_handler, mock_upload_model):
        # given
        upload_obj = AssetModel()
        mock_upload = MagicMock(spec=upload_obj)
        mock_upload.id = "any_id"

        mock_upload_model.get = MagicMock(return_value=mock_upload)

        # when
        service = BucketTriggerService(event_name="ObjectCreated:Put",
                                       asset_path="random/any_id")
        response = service.execute.__wrapped__(service)

        # then
        mock_upload_model.get.assert_called_with(hash_key="any_id")
        mock_upload.mark_received.assert_called_once()
        mock_upload.mark_deleted.assert_not_called()
        mock_exception_handler.handel_exception.assert_not_called()
        self.assertEqual(response, HTTPStatus.ACCEPTED)

    @patch('src.app.upload.bucket.AssetModel')
    @patch('src.app.upload.bucket.ExceptionHandler')
    def test_trigger_with_delete_event(self, mock_exception_handler, mock_upload_model):
        # given
        upload_obj = AssetModel()
        mock_upload = MagicMock(spec=upload_obj)
        mock_upload.id = "any_id"

        mock_upload_model.get = MagicMock(return_value=mock_upload)

        # when
        service = BucketTriggerService(event_name="ObjectRemoved:Delete",
                                       asset_path="random/any_id")
        response = service.execute.__wrapped__(service)

        # then
        mock_upload_model.get.assert_called_with(hash_key="any_id")
        mock_upload.mark_received.assert_not_called()
        mock_upload.mark_deleted.assert_called_once()
        mock_exception_handler.handel_exception.assert_not_called()
        self.assertEqual(response, HTTPStatus.ACCEPTED)

    @patch('src.app.upload.bucket.AssetModel')
    @patch('src.app.upload.bucket.ExceptionHandler')
    def test_trigger_handle_exceptions_with_unsupported_event(self, mock_exception_handler,
                                                              mock_upload_model):
        # when
        service = BucketTriggerService(event_name="any event",
                                       asset_path="random/any_id")
        response = service.execute.__wrapped__(service)

        # then
        mock_upload_model.get.assert_not_called()
        mock_upload_model.mark_received.assert_not_called()
        mock_upload_model.mark_deleted.assert_not_called()
        self.assertTrue(isinstance(
            mock_exception_handler.handel_exception.call_args[1]['exception'],
            S3UnsupportedEvent))
        self.assertEqual(response, HTTPStatus.BAD_REQUEST)

    @patch('src.app.upload.bucket.AssetModel')
    @patch('src.app.upload.bucket.ExceptionHandler')
    def test_trigger_handle_exceptions_with_uncorrect_path(self, mock_exception_handler,
                                                           mock_upload_model):
        # when
        service = BucketTriggerService(event_name="ObjectRemoved:Delete",
                                       asset_path="any id")
        response = service.execute.__wrapped__(service)

        # then
        mock_upload_model.get.assert_not_called()
        mock_upload_model.mark_received.assert_not_called()
        mock_upload_model.mark_deleted.assert_not_called()
        self.assertTrue(isinstance(
            mock_exception_handler.handel_exception.call_args[1]['exception'],
            IndexError))
        self.assertEqual(response, HTTPStatus.BAD_REQUEST)
