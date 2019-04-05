""" Authorization related business logic.
"""


class Authorizer(object):

    @classmethod
    def is_admin(cls, user_group):
        """
         this function will return true if user is admin
         :param user_group: user group
         :return: True if user is admin
         """
        if type(user_group) is list:
            return len(set(user_group) & {'admin'}) > 0
        else:
            return user_group in {'admin'}
