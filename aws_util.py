import boto3


def list_buckets(creds):
    session = boto3.Session(
        aws_access_key_id=creds.access_key_id,
        aws_secret_access_key=creds.secret_access_key,
        aws_session_token=creds.session_token
    )

    client = session.client('s3')
    response = client.list_buckets()

    return response['Buckets']
