from src.app.auth.authorizer import AuthorizerService
from src.app.auth.post import PostAuthService


def post_auth(event, context):
    """
    :param event : dict
    :param context: lambda object
    :return:
    """
    response = PostAuthService(event=event).execute()
    return response


def authorizer(event, context):
    """
    :param event: a dictionary contains { type : TOKEN | , methodArn : "ARN of lambda function",
         authorizationToken : JWT Token. }
    :param context: dict object
    :return:
    """
    policy_document = AuthorizerService(event=event).execute()
    return policy_document
