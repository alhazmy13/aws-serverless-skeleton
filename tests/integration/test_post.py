import copy
from http import HTTPStatus
import json
import random
import unittest
import uuid

from src.app.post.create import CreateService
from src.app.post.get import GetService
from src.app.post.list import ListService
from tests.data import MOCK_POST_REQUEST


class PostCreateServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.user_id = str(uuid.UUID(int=random.Random().getrandbits(128)))
        self.body = json.dumps(MOCK_POST_REQUEST)

    def test_step_1_create_service_return_200_when_the_json_body_is_valid(self):
        response = CreateService(user_sub=self.user_id, body=self.body).execute()
        self.assertEqual(response.get('statusCode'), HTTPStatus.OK)

    def test_step_3_create_service_with_different_uuids(self):
        first_response = CreateService(
            user_sub=str(uuid.UUID(int=random.Random().getrandbits(128))),
            body=self.body).execute()
        second_response = CreateService(
            user_sub=str(uuid.UUID(int=random.Random().getrandbits(128))),
            body=self.body).execute()

        self.assertEqual(first_response.get('statusCode'), HTTPStatus.OK)
        self.assertEqual(second_response.get('statusCode'), HTTPStatus.OK)
        self.assertFalse(json.loads(first_response.get('body')).get('user_sub')
                         == json.loads(second_response.get('body')).get('user_sub'))

    def test_step_4_create_service_return_400_when_request_is_invalid(self):
        request = copy.deepcopy(MOCK_POST_REQUEST)
        request['status'] = "MEH"
        response = CreateService(user_sub=self.user_id, body=json.dumps(request)).execute()
        self.assertEqual(response.get('statusCode'), HTTPStatus.BAD_REQUEST)


class PostListServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.user_id = '9929942b-a90b-443d-96bf-19393615f6d7'

    def test_list_service_return_200(self):
        response = ListService().execute()
        self.assertEqual(response.get('statusCode'), HTTPStatus.OK)

    def test_list_service_return_correct_pagination_response(self):
        response = ListService(limit=2, offset=0).execute()
        response_json = json.loads(response.get('body'))
        self.assertEqual(len(response_json), 2)


class PostGetServiceTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_service_return_200(self):
        # given
        path_param = '5943082c-f136-11e7-8919-0a6d48ff11de'

        # when
        response = GetService(path_param, '').execute()

        # then
        self.assertEqual(response.get('statusCode'), HTTPStatus.OK)

    def test_get_service_return_404(self):
        # given
        path_param = 'blah_'
        user_group = ''

        # when
        response = GetService(path_param, user_group).execute()

        # then
        self.assertEqual(response.get('statusCode'), HTTPStatus.NOT_FOUND)

    def test_get_service_admin_return_200(self):
        # given
        path_param = '5943082c-f136-11e7-8919-0a6d48ff11d2'
        user_group = 'admin'

        # when
        response = GetService(path_param, user_group).execute()

        # then
        self.assertEqual(response.get('statusCode'), HTTPStatus.OK)

    def test_get_service_when_the_user_request_a_draft_post_return_404(self):
        # given
        path_param = '5943082c-f136-11e7-8919-0a6d48ff11d2'
        user_group = ''

        # when
        response = GetService(path_param, user_group).execute()

        # then
        self.assertEqual(response.get('statusCode'), HTTPStatus.NOT_FOUND)
