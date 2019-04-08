from http import HTTPStatus

from pynamodb.exceptions import (DeleteError, DoesNotExist,
                                 GetError, TableDoesNotExist,
                                 UpdateError)
from src.app.upload.model import AssetModel, AssetState
from src.common.decorator import api_response
from src.common.exceptions import ExceptionHandler


class BucketTriggerService(object):
    """ Triggered by s3 events, object create and remove """

    def __init__(self, event_name, asset_path):
        """
        :param event_name: ObjectCreated:Put or ObjectRemoved:Delete
        :param asset_path: path of file ex: test/xxxx-xxxx-xxxx-xxx
        :return: http response
        """
        self.event_name = event_name
        self.asset_path = asset_path

    @api_response()
    def execute(self):
        """
        execute function
        :return: http response
        """
        try:
            asset_id = self.asset_path.split("/")[1]
            if 'ObjectCreated:Put' == self.event_name:
                asset = AssetModel.get(hash_key=asset_id)
                self.mark_received(asset=asset)
            elif 'ObjectRemoved:Delete' == self.event_name:
                asset = AssetModel.get(hash_key=asset_id)
                self.mark_deleted(asset=asset)
        except AssertionError as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST
        except UpdateError as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST
        except GetError as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST
        except DeleteError as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST
        except TableDoesNotExist as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST
        except DoesNotExist as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.NOT_FOUND
        except KeyError as ex:
            ExceptionHandler.handel_exception(exception=ex)
            return HTTPStatus.BAD_REQUEST
        return HTTPStatus.ACCEPTED

    @staticmethod
    def mark_received(asset):
        """
        Mark asset as having been received via the s3 objectCreated:Put event
        """
        asset.state = AssetState.RECEIVED.name
        asset.save()

    @staticmethod
    def mark_deleted(asset):
        """
        Mark asset as deleted (soft delete)
        """
        asset.state = AssetState.DELETED.name
        asset.save()
