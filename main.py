import logging
import os

from flask import Flask, jsonify, make_response

from client import test_aws_api_call

app = Flask(__name__)


@app.route('/')
def test_aws_api():
    return make_response(
        jsonify(test_aws_api_call(os.environ.get('AWS_ROLE_ARN'), os.environ.get('TARGET_AUDIENCE')), 200))


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app-flex.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
