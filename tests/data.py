"""
Test fixtures
"""

MOCK_POST_REQUEST = {
    'title': 'Title',
    'post': 'Post',
    'status': 'DRAFT'

}

MOCK_POST_RESPONSE = {
    "createdAt": "2019-04-05T00",
    "updatedAt": "2019-04-05T00",
    "post": "Post",
    "title": "Title",
    "user_sub": "20aedd95-4e39-8f51-7103-2d457b883c00",
    "status": "DRAFT",
    "id": "ffadd78f-2d0e-40dd-8fb6-1e6ee26a3091"
}

MOCK_COGNITO_POST_EVENT = {
    "userName": "anyUser",
    "request": {
        "userAttributes": {
            "sub": "9929942b-a90b-443d-96bf-19393615f6d7",
            "email_verified": "true",
            "cognito:user_status": "CONFIRMED",
            "phone_number_verified": "false",
            "given_name": "Any",
            "email": "test@domain.com"
        }
    }
}

MOCK_Custom_authorizer = {
    'type': 'TOKEN',
    'methodArn': 'arn:aws:execute-api:eu-west-1:000000000000:randomkey/dev/GET/function',
    'authorizationToken':
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTI5OTQyYi1hOTBiLTQ0M'
        '2QtOTZiZi0xOTM5MzYxNWY2ZDciLCJjb2duaXRvOmdyb3VwcyI6W10sImNvZ25pdG86dXNlcm5hbWUiOiJ'
        'VU0VSTkFNRSIsImF1ZCI6IkFVRF9OVU1CRVIiLCJuYW1lIjoiVXNlciJ9.opOkjGvHQ'
        'RlJ-VyNP-bfTOlu_-lHmBUjzeBe8XfkoD0'
}
