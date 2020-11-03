#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
#   $ python3 -m pip install Flask python-dotenv
#

import sys

import flask
import requests

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

upstream = app.config['UPSTREAM']

services = {
    'user': [app.config['USER_0'], app.config['USER_1'], app.config['USER_2']],
    'timeline': [app.config['TIMELINES_0'], app.config['TIMELINES_1'], app.config['TIMELINES_2']],
}


def rotate_service_hosts(service_name):
    # Cycle the service's hosts name for round robin.
    service_hosts = services[service_name]
    service_hosts.append(service_hosts.pop(0))
    return service_hosts


@app.route('/<service>/<query>', methods=['GET', 'POST'])
def call_service(service, query=''):
    service_hosts = rotate_service_hosts(service)
    service_url = service_hosts[0] + '/' + service + query
    response = requests.request(method=flask.request.method, url=service_url, data=flask.request.get_json())
    if 500 <= response.status_code <= 599:
        service_hosts.pop(0)
    return str(response.status_code)


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
