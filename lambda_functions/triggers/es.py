import os

from src.app.trigger.es import DynamoToEsService
from src.common.log import get_logger


def dynamo_to_es(event, context):
    """
    :param event: dict
    :param context: dict
    :return: None
    """
    try:
        return DynamoToEsService(event=event,
                                 es_endpoint=os.environ["ES_ENDPOINT"],
                                 region=os.environ["REGION"]).execute()
    except Exception as ex:
        get_logger().error(ex)
