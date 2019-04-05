from datetime import datetime
import os

from pynamodb.attributes import (UnicodeAttribute, UTCDateTimeAttribute)
from pynamodb.models import Model


class UserModel(Model):
    """
    A DynamoDB User
    """

    class Meta:
        table_name = os.environ.get("DYNAMODB_USER_TABLE")
        region = os.environ.get("REGION")
        if os.environ.get('DYNAMODB_HOST') is not None:
            host = os.environ.get("DYNAMODB_HOST")

    id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    given_name = UnicodeAttribute()
    username = UnicodeAttribute()
    createdAt = UTCDateTimeAttribute(null=False, default=datetime.utcnow)
    updatedAt = UTCDateTimeAttribute(null=False, default=datetime.utcnow)

    @classmethod
    def create(cls, event):
        return UserModel(event.get('request').get('userAttributes').get('sub'),
                         given_name=event
                         .get('request')
                         .get('userAttributes')
                         .get('given_name'),
                         email=event
                         .get('request')
                         .get('userAttributes')
                         .get('email'),
                         username=event.get('userName'))
