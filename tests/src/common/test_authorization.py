import unittest

from src.common.authorization import Authorizer


class TestAuthorizer(unittest.TestCase):

    def test_is_admin_with_regular_user(self):
        self.assertFalse(Authorizer.is_admin(["mygroup"]))
        self.assertFalse(Authorizer.is_admin("mygroup"))

    def test_is_admin_success(self):
        self.assertTrue(Authorizer.is_admin(["admin"]))
        self.assertTrue(Authorizer.is_admin("admin"))
