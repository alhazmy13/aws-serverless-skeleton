import os
import random
import uuid

import boto3
from botocore.client import Config
from src.app.upload.model import AssetModel
from src.common.decorator import api_response


class CreatePreSignedUrlService(object):
    """ Service to create new Asset object and save it in DynamoDB """

    def __init__(self, user_sub):
        """
        :param user_sub: user is as string
        :return: http response
        """
        self.user_sub = user_sub

    @api_response()
    def execute(self):
        """
        execute function
        :return: http response
        """
        asset = self._create_upload_asset()
        upload_url = self._get_upload_url(key=self._get_key(asset=asset),
                                          ttl=os.environ['S3_UPLOAD_URL_DEFAULT_TTL'],
                                          region=os.environ['REGION'],
                                          bucket=os.environ['S3_UPLOAD_BUCKET'])
        response = {
            'upload_url': upload_url,
            'id': asset.id
        }
        return response

    @staticmethod
    def _create_upload_asset():
        """
         function to create new Asset object with random hash key
         :return: http response
         """
        _random = random.Random()
        _random.seed(0)
        asset = AssetModel()
        asset.id = uuid.UUID(int=_random.getrandbits(128)).__str__()
        asset.save()
        return asset

    def _get_upload_url(self, key, region, bucket, ttl=300):
        """
        :param asset: Asset object
        :param ttl: url duration in seconds
        :return: a temporary preSigned PUT url
        """
        s3 = boto3.client('s3',
                          region,
                          config=Config(signature_version='s3v4'))

        # 'ServerSideEncryption': 'aws:kms'
        put_url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=ttl,
            HttpMethod='PUT')
        return put_url

    def _get_key(self, asset):
        return u'{}/{}'.format(self.user_sub, asset.id)
