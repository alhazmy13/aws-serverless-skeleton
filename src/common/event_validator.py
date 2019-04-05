import os

""" common function to extract values from event request
"""


class EventValidator(object):
    @classmethod
    def get_path_parameters_from_event(cls, event, key='id'):
        """
         this function will return the value for any key from pathParameters
         :param event: event request
         :param key: key for your value
         :return: the value of your key from pathParameters
         """
        return event.get('pathParameters').get(key)

    @classmethod
    def get_user_sub_from_event(cls, event):
        """
        this function will return the user sub event request
        :param event: event request
        :return: the user sub
        """
        # Workaround until we found a solution to deploy cognito locally
        if os.environ.get('IS_OFFLINE') is not None:
            return os.environ.get('LOCAL_USER_ID')
        request_context = event.get('requestContext')
        authorizer = request_context.get('authorizer')
        claims = authorizer.get('claims')
        if claims is not None:
            return claims.get('sub')
        return authorizer.get('principalId')

    @classmethod
    def get_user_mobile_from_event(cls, event):
        """
        this function will return the user sub event request
        :param event: event request
        :return: the user sub
        """
        # Workaround until we found a solution to deploy cognito locally
        if os.environ.get('IS_OFFLINE') is not None:
            return os.environ.get('LOCAL_USER_MOBILE')
        request_context = event.get('requestContext')
        authorizer = request_context.get('authorizer')
        claims = authorizer.get('claims')
        if claims is not None:
            return claims.get('phone_number')
        return authorizer.get('principalId')

    @classmethod
    def get_query_from_event(cls, event, key):
        """
        this function will return the value for any key from queryStringParameters
        :param event: event request
        :param key: key for your value
        :return: the value of your key from queryStringParameters
        """
        query = event.get('queryStringParameters')
        if query is None:
            return None
        return query.get(key)
