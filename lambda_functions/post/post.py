from src.app.post.create import CreateService
from src.app.post.get import GetService
from src.app.post.list import ListService
# from src.app.post.update import UpdateService
# from src.app.post.delete import DeleteService
from src.common.decorator import gateway_request_interceptor
from src.common.event_validator import EventValidator
from src.common.jwt_validator import JwtValidator


@gateway_request_interceptor
def get(event, context):
    """
    :param event : dict
    :param context: lambda object
    :return:
    """
    response = GetService(
        path_param=EventValidator.get_path_parameters_from_event(event=event),
        user_group=JwtValidator.get_user_group_from_id_token(event=event)) \
        .execute()
    return response


@gateway_request_interceptor
def create(event, context):
    """
    :param event : dict
    :param context: lambda object
    :return:
    """
    response = CreateService(
        body=event['body'],
        user_sub=EventValidator.get_user_sub_from_event(event=event)) \
        .execute()
    return response


def list(event, context):
    """
    :param event : dict
    :param context: lambda object
    :return:
    """
    response = ListService(
        limit=EventValidator.get_query_from_event(event=event, key='limit'),
        offset=EventValidator.get_query_from_event(event=event, key='offset')) \
        .execute()
    return response

# @gateway_request_interceptor
# def delete(event, context):
#     """
#     :param event : dict
#     :param context: lambda object
#     :return:
#     """
#     response = DeleteService(
#         path_param=EventValidator.get_path_parameters_from_event(event=event)) \
#     .execute()
#     return response


# @gateway_request_interceptor
# def update(event, context):
#     """
#     :param event : dict
#     :param context: lambda object
#     :return:
#     """
#     response = UpdateService(
#         user_id=EventValidator.get_user_sub_from_event(event=event),
#         path_param=EventValidator.get_path_parameters_from_event(event=event),
#         body=event['body']) \
#         .execute()
#     return response
