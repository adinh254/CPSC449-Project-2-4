#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
#   $ python3 -m pip install Flask python-dotenv
#

import sys

from flask_api import status
import json
import requests
import flask
import base64

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

upstream = app.config['UPSTREAM']

services = {}


@app.before_first_request
def ready():
    gateway_authenticator = app.config['USER_0'] + '/user/auth'
    app.config['AUTH_SERVER'] = gateway_authenticator
    print(f'Authentication Server: {gateway_authenticator}')
    user_hosts = [app.config['USER_0'], app.config['USER_1'], app.config['USER_2']]
    user_exclude = {'create'}
    add_service('user', auth_required=True, auth_exclude_paths=user_exclude, hosts=user_hosts)

    timeline_hosts = [app.config['TIMELINES_0'], app.config['TIMELINES_1'], app.config['TIMELINES_2']]
    add_service('timeline', auth_required=True, hosts=timeline_hosts)
    print('Server Ready!')


@app.route('/')
def health_check():
    return f'Server is healthy!', status.HTTP_200_OK


def rotate_hosts(service_name):
    # Cycle the service's hosts name for round robin.
    hosts = services[service_name]['hosts']
    hosts.append(hosts.pop(0))
    return hosts


@app.route('/<service>/<query>', methods=['GET', 'POST'])
def call_service(service, query=None):
    if service not in services:
        return f'ERROR HTTP 404: Service {service} does not exist.', status.HTTP_404_NOT_FOUND

    url_path = '/' + '/'.join(filter(None, (service, query)))
    hosts = services[service]['hosts']

    # Basic authorization
    if auth_required('user', query):
        auth_header = flask.request.headers.get('authorization')
        if not auth_header or not auth_header.startswith('Basic'):
            return f'ERROR HTTP 401: Authorization headers are missing or are not in Basic format.', status.HTTP_401_UNAUTHORIZED
        access_token = auth_header[len('Basic '):]
        print(access_token)
        username_password = base64.b64decode(access_token).decode('utf-8')
        print(username_password)
        separator_idx = username_password.find(':')

        username = username_password[:separator_idx]
        password = username_password[separator_idx + 1:]
        print(username, password)
        if not username and password:
            return f'ERROR HTTP 401: Username or password not supplied.', status.HTTP_401_UNAUTHORIZED
        if not check_credentials(username, password):
            return f'ERROR HTTP 401: Invalid username or password.', status.HTTP_401_UNAUTHORIZED
        print('Login Success!')

    while len(hosts) > 0:
        current_host = hosts[0]
        print(f'Connecting to host: {current_host}.')
        request_url = current_host + url_path
        print(request_url)
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


def auth_required(service, query_path):
    return services[service]['auth_required'] and (query_path not in services[service]['auth_exclude'])


def check_credentials(username, password):
    auth_data = {'username': username, 'password': password}
    print(app.config['AUTH_SERVER'])
    try:
        response = requests.get(url=app.config['AUTH_SERVER'], json=auth_data)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as errh:
        status_code = errh.response.status_code
        if status_code == 401:
            return False
        raise f'ERROR HTTP {status_code}: Request to authentication server failed.'
    except requests.exceptions.ConnectionError:
        raise 'ERROR Connection: {auth_url} Authentication server is not responding.'



def add_service(service_name, auth_required=True, auth_exclude_paths = {}, hosts=[]):
    # Adds service with data to the load balancer.
    services[service_name] = {
        'auth_required' : auth_required,
        'auth_exclude' : auth_exclude_paths,
        'hosts' : hosts,
    }


def service_add_auth_exclusion(service_name, url_path):
    # Adds an exclusion path to ignore authorization for the respective service.
    services[service_name]['auth_required'].add(url_path)


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
