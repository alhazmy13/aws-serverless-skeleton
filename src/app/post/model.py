from datetime import datetime
import os
import uuid

from pynamodb.attributes import (UnicodeAttribute, UTCDateTimeAttribute)
from pynamodb.models import Model
from src.app.post.validation import validate_post_request


class PostModel(Model):
    """
    A DynamoDB post table
    """

    id = UnicodeAttribute(hash_key=True)
    user_sub = UnicodeAttribute()
    post = UnicodeAttribute()
    title = UnicodeAttribute()
    status = UnicodeAttribute()
    createdAt = UTCDateTimeAttribute(null=False, default=datetime.utcnow)
    updatedAt = UTCDateTimeAttribute(null=False, default=datetime.utcnow)

    class Meta:
        table_name = os.environ.get("DYNAMODB_POST_TABLE")
        region = os.environ.get("REGION")
        if os.environ.get('DYNAMODB_HOST') is not None:
            host = os.environ.get("DYNAMODB_HOST")

    @classmethod
    @validate_post_request
    def create(cls, user_sub, data):
        return PostModel(str(uuid.uuid4()),
                         user_sub=user_sub,
                         post=data.get('post'),
                         title=data.get('title'),
                         status=data.get('status'))
