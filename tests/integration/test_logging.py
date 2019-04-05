import unittest

from src.common.log import get_logger
from testfixtures import LogCapture


class TestLogging(unittest.TestCase):

    def test_logger_when_config_file_exist(self):
        '''
        when config file is there, then we expect a logger based
        on specified configuration
        '''
        prod_logger = get_logger(logger_type='prod')
        datadog_logger = get_logger(logger_type='datadog')
        self.assertEqual(prod_logger.logger.name, 'prod')
        self.assertEqual(prod_logger.logger.level, 20)
        self.assertEqual(datadog_logger.logger.level, 20)
        self.assertEqual(datadog_logger.logger.name, 'datadog')

    def test_logger_format_for_datadog(self):
        '''
        test that datalog logger is going to write messages in the right format:
        '''
        datadog_logger = get_logger(logger_type='datadog')
        with LogCapture(('datadog')) as log_capture:
            datadog_logger.extra = {
                **datadog_logger.extra,
                **{
                    'metric_value': '1',
                    'metric_type': 'count',
                    'metric_name': 'page_view',
                    "tag_value": "#function:get_id"
                }
            }
            datadog_logger.info("")

            self.assertEqual(len(log_capture.records), 1)
            record = log_capture.records[-1]
            self.assertEqual(record.getMessage(), '')
            self.assertEqual(record.metric_value, '1')
            self.assertEqual(record.metric_type, 'count')
            self.assertEqual(record.metric_name, 'page_view')
            self.assertEqual(record.tag_value, '#function:get_id')
