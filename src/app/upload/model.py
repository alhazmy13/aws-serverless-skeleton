from datetime import datetime
from enum import Enum
import os

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

    def __str__(self):
        return 'id:{}, state:{}'.format(self.id, self.state)

    def save(self, conditional_operator=None, **expected_values):
        self.updatedAt = datetime.utcnow()
        super(AssetModel, self).save()
