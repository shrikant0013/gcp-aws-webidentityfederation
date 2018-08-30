import boto3
from collections import namedtuple


class AWSFederation(object):
    def __init__(self, role_arn):
        self.role_arn = role_arn
        self.role_session = "google-federate"

        self.BasicSessionCredentials = namedtuple('BasicSessionCredentials', ['access_key_id', 'secret_access_key',
                                                                              'session_token'])

    def get_credentials(self, token):
        client = boto3.client('sts')
        response = client.assume_role_with_web_identity(
            RoleArn=self.role_arn,
            RoleSessionName=self.role_session,
            WebIdentityToken=token,
        )
        access_key_id = response['Credentials']['AccessKeyId']
        secret_access_key = response['Credentials']['SecretAccessKey']
        session_token = response['Credentials']['SessionToken']

        session_credentials = self.BasicSessionCredentials(access_key_id, secret_access_key, session_token)
        return session_credentials
