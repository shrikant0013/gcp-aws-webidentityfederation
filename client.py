import os
import json
import jwt as pyjwt

from aws_util import list_buckets
from creds_webidentity import AWSFederation
from oidc_token_maker import OIDCTokenMaker


def test_aws_api_call(aws_role_arn, target_audience):
    oidc = OIDCTokenMaker(target_audience=target_audience)
    token = oidc.make_token()

    result = {
        'token': pyjwt.decode(token, verify=False)
    }
    web_id = AWSFederation(aws_role_arn)
    buckets = list_buckets(web_id.get_credentials(token))
    bucket_names = []

    for bucket in buckets:
        bucket_names.append(bucket.get('Name'))
    result['output'] = bucket_names
    return result


if __name__ == '__main__':
    print(json.dumps(test_aws_api_call(os.environ.get('AWS_ROLE_ARN'), os.environ.get('TARGET_AUDIENCE')), indent=2))