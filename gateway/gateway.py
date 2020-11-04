#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
#   $ python3 -m pip install Flask python-dotenv
#

import sys

from flask_api import status
import flask
import requests

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

upstream = app.config['UPSTREAM']

services = {
    'user': [app.config['USER_0'], app.config['USER_1'], app.config['USER_2']],
    'timeline': [app.config['TIMELINES_0'], app.config['TIMELINES_1'], app.config['TIMELINES_2']],
}


@app.route('/')
def health_check():
    return f'Server is healthy!', status.HTTP_200_OK


def rotate_hosts(service_name):
    # Cycle the service's hosts name for round robin.
    hosts = services[service_name]
    hosts.append(hosts.pop(0))
    return hosts


@app.route('/<service>', methods=['GET', 'POST'])
@app.route('/<service>/<query>', methods=['GET', 'POST'])
def call_service(service, query=None):
    if service not in services:
        return f'ERROR HTTP 404: Service {service} does not exist.', status.HTTP_404_NOT_FOUND

    url_path = '/' + '/'.join(filter(None, (service, query)))
    hosts = services[service]

    while len(hosts) > 0:
        current_host = hosts[0]
        print(f'Connecting to host: {current_host}.')
        request_url = current_host + url_path
        try:
            response = requests.request(method=flask.request.method, url=request_url, json=flask.request.get_json())
            hosts = rotate_hosts(service)
            response.raise_for_status()
            return response.json(), status.HTTP_200_OK
        except requests.exceptions.HTTPError as errh:
            status_code = errh.response.status_code
            return f'ERROR HTTP {status_code}: {current_host} request failed.'
        except requests.exceptions.ConnectionError:
            removed_host = hosts.pop(0)
            print(f'ERROR Connection: {removed_host} is not responding and was removed from the server pool.')
    return 'ERROR HTTP 502: Unable to get valid responses from any servers.', status.HTTP_502_BAD_GATEWAY


@app.errorhandler(404)
def route_page(err):

    try:
        response = requests.request(
            flask.request.method,
            upstream + flask.request.full_path,
            data=flask.request.get_data(),
            headers=flask.request.headers,
            cookies=flask.request.cookies,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        app.log_exception(sys.exc_info())
        return flask.json.jsonify({
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }), 503

    headers = remove_item(
        response.headers,
        'Transfer-Encoding',
        'chunked'
    )

    return flask.Response(
        response=response.content,
        status=response.status_code,
        headers=headers,
        direct_passthrough=True,
    )


def remove_item(d, k, v):
    if k in d:
        if d[k].casefold() == v.casefold():
            del d[k]
    return dict(d)
