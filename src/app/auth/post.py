from src.app.auth.model import UserModel
from src.common.exceptions import ExceptionHandler


class PostAuthService(object):
    """ Amazon Cognito invokes this trigger to initiate the custom authentication flow. """

    def __init__(self, event):
        """
        :param self.event: dict
        :return: dict
        """
        self.event = event

    def execute(self):
        try:
            user = self.get_user(
                user_sub=self.get_user_attributes().get('sub'))
            self.update_current_user_record(
                user=user,
                given_name=self.get_user_attributes().get('given_name'),
                email=self.get_user_attributes().get('email'))
        except AttributeError as ex:
            ExceptionHandler.handel_exception(ex)
        except UserModel.DoesNotExist:
            user = UserModel.create(event=self.event)
            user.save()
        return self.event

    def get_user_attributes(self):
        return self.event.get('request').get('userAttributes')

    @staticmethod
    def get_user(user_sub):
        return UserModel.get(user_sub)

    @staticmethod
    def update_current_user_record(user, given_name, email):
        user.update(actions=[
            UserModel.given_name.set(given_name),
            UserModel.email.set(email),
        ])
        return user
