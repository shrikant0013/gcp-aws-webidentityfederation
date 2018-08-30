import logging


def make_fetch(url, data=None, headers=None, method=None):
    try:
        from google.appengine.api import urlfetch
    except ImportError:
        raise EnvironmentError('The App Engine APIs are not available.')

    urlfetch.set_default_fetch_deadline(60)
    rpc = urlfetch.create_rpc()
    if method == "POST":
        urlfetch.make_fetch_call(rpc, url, method="POST",
                                 headers=headers, payload=data,
                                 validate_certificate=True)
    elif method == "GET":
        urlfetch.make_fetch_call(rpc, url)

    try:
        result = rpc.get_result()
        if result.status_code == 200:
            logging.info("Successful urlfetch for {}".format(method))
            text = result.content
            return text
        else:
            logging.error('Returned status code {}'.format(result.status_code))
            logging.error(result)

    except urlfetch.DownloadError as e:
        logging.error(str(e))

    except urlfetch.Error as e:
        logging.error(str(e))


def make_request(url, data=None, headers=None, method=None):
    try:
        import requests
    except ImportError:
        raise EnvironmentError('Requests module is required for this environment')
    try:
        response = None
        if method == "POST":
            response = requests.post(url, data=data)

        elif method == "GET":
            response = requests.get(url)

        if response and response.status_code == 200:
            logging.info("Successful request for {}".format(method))
            return response.text

        logging.error("Returned status code {}".format(response.status_code if response else "<Unknown>"))
        response.raise_for_status()

    except requests.exceptions.HTTPError as http_error:
        logging.error(http_error.response.status_code)
