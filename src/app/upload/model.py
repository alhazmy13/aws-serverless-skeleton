from datetime import datetime
from enum import Enum
import os
import random
import uuid

from pynamodb.attributes import (UnicodeAttribute, UTCDateTimeAttribute)
from pynamodb.models import Model


class AssetState(Enum):
    """
    Manage asset states in dynamo with a string field
    Could have used an int as well, or used a custom serializer which is a bit cleaner.
    """
    CREATED = 1
    RECEIVED = 2
    UPLOADED = 3
    DELETED = 4


class AssetModel(Model):
    class Meta:
        table_name = os.environ.get("DYNAMODB_UPLOAD_TABLE")
        region = os.environ.get("REGION")
        if os.environ.get('DYNAMODB_HOST') is not None:
            host = os.environ.get("DYNAMODB_HOST")

    id = UnicodeAttribute(hash_key=True)
    state = UnicodeAttribute(null=False, default=AssetState.CREATED.name)
    createdAt = UTCDateTimeAttribute(null=False, default=datetime.utcnow)
    updatedAt = UTCDateTimeAttribute(null=False, default=datetime.utcnow)

    @classmethod
    def create(cls):
        """
         function to create new Asset object with random hash key
         :return: asset model
         """
        _random = random.Random()
        _uuid = uuid.UUID(int=_random.getrandbits(128)).__str__()
        return AssetModel(_uuid)

    def mark_received(self):
        """
        Mark asset as having been received via the s3 objectCreated:Put event
        """
        return self.update(actions=[
            AssetModel.state.set(AssetState.RECEIVED.name)
        ])

    def mark_deleted(self):
        """
        Mark asset as deleted (soft delete)
        """
        return self.update(actions=[
            AssetModel.state.set(AssetState.DELETED.name)
        ])
