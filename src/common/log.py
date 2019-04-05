import logging.config
import os
import pathlib


import src.common.context
import yaml


class _LogOptions(object):

    def __init__(self, config_file):
        self.config_file = config_file

    def _read_options(self):
        try:
            with open(self.config_file, 'rt', encoding='utf8') as file_obj:
                return file_obj.read()
        except IOError as ioException:
            print("IOError reading config file {0}:{1}".format(self.config_file, ioException))

    def setup(self):
        log_options_stream = self._read_options()
        if log_options_stream:
            config_as_yaml = yaml.safe_load(log_options_stream)
            logging.config.dictConfig(config_as_yaml)
            return True
        else:
            logging.basicConfig(level="INFO")
            logging.warning("logging setup has failed, going with basic root")


def _initialize():
    config_file_location = 'config/resource/logging.yaml'

    # get current file abs path
    current_file_location = pathlib.Path(__file__).resolve()
    # get root directory full path
    root_directory = current_file_location.parents[2]
    # join both paths to create final file abs path
    abs_config_file_path = root_directory.joinpath(config_file_location)

    # setup logging options
    log_options = _LogOptions(abs_config_file_path)
    log_options.setup()


_initialize()


def get_logger(logger_type=os.environ.get('STAGE', 'dev')):
    context_data = {'request_id': src.common.context.REQUEST_ID}
    logger = logging.getLogger(logger_type)
    logger = logging.LoggerAdapter(logger, context_data)
    return logger
