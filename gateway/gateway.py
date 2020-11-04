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


def rotate_hosts(service_name):
    # Cycle the service's hosts name for round robin.
    hosts = services[service_name]
    hosts.append(hosts.pop(0))
    return hosts


@app.route('/<service>', methods=['GET', 'POST'])
@app.route('/<service>/<query>', methods=['GET', 'POST'])
def call_service(service, query=None):
    if service in services:
        hosts = services[service]
        if len(hosts) < 1:
            return f'Service {service} has no hosts.', status.HTTP_502_GATEWAY

        current_host = hosts[0]
        hosts = rotate_hosts(service)
        service_url = current_host + '/' + service
        if query != None:
            service_url += '/' + query

        while len(hosts) > 0:
            try:
                response = requests.request(method=flask.request.method, url=service_url, json=flask.request.get_json())
                return response.json(), status.HTTP_200_OK
            except requests.exceptions.RequestException as e:
                status_code = e.response.status_code
                if 500 <= status_code <= 599:
                    removed_host = service_hosts.pop(0)
                    print(f'Connection Refused: Removed {removed_host}, from service host pool.')
                else:
                    return e, status_code
    return f'Service {service} does not exist.', status.HTTP_404_NOT_FOUND


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
