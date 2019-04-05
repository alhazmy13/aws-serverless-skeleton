import datetime
import json

from boto3.dynamodb.types import TypeDeserializer


class PynamoDbEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'attribute_values'):
            return obj.attribute_values
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class ElasticSearchEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '_l_'):
            return obj._l_
        return obj.__dict__


class StreamTypeDeserializer(TypeDeserializer):
    """ Subclass of boto's TypeDeserializer for DynamoDB to adjust for DynamoDB Stream format."""

    def _deserialize_n(self, value):
        return float(value)

    def _deserialize_b(self, value):
        return value  # Already in Base64
