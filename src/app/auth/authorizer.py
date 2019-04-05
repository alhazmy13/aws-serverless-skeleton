from src.app.auth.auth_policy import AuthPolicy
from src.common.jwt_validator import JwtValidator


class AuthorizerService(object):
    def __init__(self, event):
        """
        :param event : a dictionary contains { type : TOKEN |,
         methodArn : "ARN of lambda function",
         authorizationToken : JWT Token. }
        """
        self.event = event

    def execute(self):
        """
        execute function
        :return: policy document to API gateway with permission to invoke lambda
        """
        policy_document = self.auth_authorizer_check()
        return policy_document

    def auth_authorizer_check(self):
        """
        :return:
        """

        """
        Getting token are coming with request in header from
        event dictionary where the token is JWT token
        """
        token = self.event.get('authorizationToken')
        user_id = JwtValidator.get_user_id(token=token)

        """ validate the incoming token """
        """and produce the principal user identifier associated with the token"""

        """this could be accomplished in a number of ways:"""
        """1. Call out to OAuth provider"""
        """2. Decode a JWT token inline"""
        """3. Lookup in a self-managed DB"""
        principal_id = user_id

        """ you can send a 401 Unauthorized response to the client by failing like so: """
        """ raise Exception('Unauthorized') """

        """
        if the token is valid, a policy must be generated which
        will allow or deny access to the client
        if access is denied, the client will recieve a 403 Access Denied response
        if access is allowed, API Gateway will proceed with
        the backend integration configured on the method that was called
        this function must generate a policy that is associated with
        the recognized principal user identifier.
        depending on your use case, you might store policies in a DB,
        or generate them on the fly
        """

        """keep in mind, the policy is cached for 5 minutes by default
        (TTL is configurable in the authorizer) and will apply to subsequent calls
        to any method/resource in the RestApi made with the same token
        """

        """the example policy below denies access to all resources in the RestApi"""
        method_arn = self.event.get('methodArn')
        tmp = method_arn.split(':')

        api_gateway_arn_tmp = tmp[5].split('/')
        aws_account_id = tmp[4]

        policy = AuthPolicy(principal=principal_id, aws_account_id=aws_account_id)
        policy.rest_api_id = api_gateway_arn_tmp[0]
        policy.region = tmp[3]
        policy.stage = api_gateway_arn_tmp[1]
        policy.allow_all_methods()
        """ policy.allowMethod(HTTPMethod.GET, "/common") """
        # Finally, build the policy
        auth_response = policy.build()

        return auth_response
