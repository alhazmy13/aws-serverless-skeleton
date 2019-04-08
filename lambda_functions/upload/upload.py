from src.app.upload.bucket import BucketTriggerService
from src.app.upload.create import CreatePreSignedUrlService
from src.common.event_validator import EventValidator


def create(event, context):
    response = CreatePreSignedUrlService(
        user_sub=EventValidator.get_user_sub_from_event(event=event)) \
        .execute()
    return response


def bucket(event, context):
    """
    Triggered by s3 events, object create and remove

    """
    event_name = event['Records'][0]['eventName']
    asset_path = event['Records'][0]['s3']['object']['key']
    response = BucketTriggerService(event_name=event_name,
                                    asset_path=asset_path).execute()
    return response
