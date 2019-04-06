from enum import Enum
import os

from jose import jwt


class JwtValidator(object):
    """ Handles validation of a JWT web-token passed by the client
    """

    @classmethod
    def get_token_from_event(cls, event):
        headers = event.get('headers')
        authorization = headers.get('Authorization')
        return authorization

    @classmethod
    def get_user_group_from_id_token(cls, event):
        # Workaround until we found a solution to deploy cognito locally
        if os.environ.get('IS_OFFLINE') is not None:
            return [os.environ.get('LOCAL_USER_GROUP')]
        token = cls.get_token_from_event(event)
        payload = jwt.get_unverified_claims(token)
        return payload.get('cognito:groups')

    @classmethod
    def is_have_an_access(cls, event, group):
        if not Groups.verify(group):
            raise ValueError("Group should be instance of Groups enum")
        user_group = cls.get_user_group_from_id_token(event)
        if user_group is None:
            return False
        return group.value in user_group

    @classmethod
    def get_user_id(cls, token):
        payload = jwt.get_unverified_claims(token)
        return payload.get('sub')


class Groups(Enum):
    ADMIN = "admin"

    @classmethod
    def verify(cls, other):
        return issubclass(other.__class__, cls)
