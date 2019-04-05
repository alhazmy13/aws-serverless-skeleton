import unittest
from unittest.mock import call, MagicMock, patch


import src.common.context
from src.common.log import _LogOptions, get_logger


class TestLog(unittest.TestCase):
    @patch('src.common.log.logging')
    def test_get_logger(self, mock_logging):
        # given
        src.common.context.REQUEST_ID = "12345"

        mock_logger = MagicMock()
        mock_logging.getLogger = MagicMock(return_value=mock_logger)

        # when
        logger = get_logger('my stage')

        # then
        self.assertEqual(mock_logging.getLogger.mock_calls, [
            call('my stage'),
        ])
        self.assertEqual(mock_logging.LoggerAdapter.mock_calls, [
            call(mock_logger, {'request_id': '12345'})
        ])
        self.assertTrue(logger is not None)

    def test_initialization_invalid_file(self):
        # given
        log_options = _LogOptions("dummy")

        # when
        success = log_options.setup()

        # then
        self.assertFalse(success)

    def test_initialization_success(self):
        # given
        log_options = _LogOptions('config/resource/logging.yaml')

        # when
        success = log_options.setup()

        # then
        self.assertTrue(success)
