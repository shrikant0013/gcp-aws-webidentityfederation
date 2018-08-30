import logging
import sys
import time
import urllib
import json
from google.auth import default
from google.auth import jwt
from google.auth.exceptions import RefreshError
from google.auth.iam import Signer
from google.auth.transport.requests import Request

import rest_util

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

CRED_LIFETIME_DEFAULT_SECONDS = 3600
JWT_BEARER_TOKEN_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"
OAUTH_TOKEN_URI = "https://www.googleapis.com/oauth2/v4/token"
CLAIM_ISSUER = "iss"
CLAIM_ISSUED_AT = "iat"
CLAIM_EXPIRE = "exp"
CLAIM_AUDIENCE = "aud"
CLAIM_SCOPE = "scope"
TARGET_AUDIENCE = "target_audience"


class OIDCTokenMaker(object):
    def __init__(self, target_audience):
        self._service_account = None
        self._project_id = None
        self._signer = None
        self.target_audience = target_audience
        self._credentials, self._project_id = default(scopes=['https://www.googleapis.com/auth/userinfo.email'])

        try:
            self._credentials.refresh(Request())
            if self._credentials.service_account_email and self._credentials.service_account_email != 'default':
                self._service_account = self._credentials.service_account_email

                logging.info("Found {} as identity of environment".format(self._service_account))
            logging.info(self._credentials.service_account_email)

        except (AttributeError, RefreshError) as e:
            logging.error(e)
            logging.error("Failed to retrieve service account email from credentials")

        try:
            if self._credentials.signer:
                self._signer = self._credentials.signer
            else:
                self._signer = Signer(Request(), self._credentials, self._service_account)

        except AttributeError as e:
            logging.error(e)
            self._signer = Signer(Request(), self._credentials, self._service_account)

        if not self._service_account or not self._project_id or not self._signer:
            raise EnvironmentError('Failed to find credentials for environment')

    @property
    def service_account_email(self):
        return self._service_account

    @property
    def project_id(self):
        return self._project_id

    def make_token(self):
        signed_jwt = self._get_signed_jwt()
        url = "https://www.googleapis.com/oauth2/v4/token"
        data = {"grant_type": JWT_BEARER_TOKEN_GRANT_TYPE,
                "assertion": signed_jwt}
        response = "{}"
        try:
            from google.appengine.api import app_identity
            if app_identity:
                response = rest_util.make_fetch(url, data=urllib.urlencode(data),
                                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                                method="POST")
        except ImportError:
            logging.debug("Looking for non GAE std environment in make token")
            response = rest_util.make_request(url, data=data, headers=None, method="POST")
        try:
            result_dict = json.loads(response)
            if result_dict and 'id_token' in result_dict:
                id_token = result_dict.get('id_token')
                return id_token
            else:
                logging.error("Failed to retrieve id token from Google")
        except TypeError as e:
            if response and response.text:
                logging.error(response.text)
            logging.error("Something went wrong with input to signjwt {}".format(e))
            raise e

    def _get_signed_jwt(self):

        now = int(time.time())
        exp = now + CRED_LIFETIME_DEFAULT_SECONDS
        svc_account = self._service_account
        payload = {
            # The issuer must be the service account email.
            CLAIM_ISSUER: svc_account,
            # CLAIM_SCOPE: svc_account,
            # The audience must be the auth token endpoint's URI
            CLAIM_AUDIENCE: OAUTH_TOKEN_URI,

            TARGET_AUDIENCE: self.target_audience,

            CLAIM_ISSUED_AT: now,
            CLAIM_EXPIRE: exp
        }

        token = jwt.encode(self._signer, payload)
        return token


