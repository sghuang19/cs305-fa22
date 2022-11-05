import json
import random
import string
from typing import *
import config
import mimetypes
from framework import HTTPServer, HTTPRequest, HTTPResponse


def random_string(length=20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def default_handler(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    response.status_code, response.reason = 404, 'Not Found'
    print(f"calling default handler for url {request.request_target}")


def task2_data_handler(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    from os.path import exists, getsize
    path = request.request_target[1:]  # remove leading '/' for relative path
    if exists(path):
        response.status_code, response.reason = 200, 'OK'
        mimetype, _ = mimetypes.guess_type(path)
        if mimetype:
            response.add_header('Content-Type', mimetype)
        response.add_header('Content-Length', str(getsize(path)))
        if request.method == 'GET':
            with open(path, 'rb') as f:
                response.body = f.read()
    else:
        response.status_code, response.reason = 404, 'Not Found'
        response.add_header('Content-Length', '0')

    response.write_all()


def task3_json_handler(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    response.status_code, response.reason = 200, 'OK'
    if request.method == 'POST':
        binary_data = request.read_message_body()
        obj = json.loads(binary_data)
        server.task3_data = obj['data']
    else:
        obj = {'data': server.task3_data}
        response.body = json.dumps(obj).encode()
        response.add_header('Content-Type', 'application/json')
        response.add_header('Content-Length', str(len(response.body)))
    if request.method == 'HEAD':
        response.body = b''

    response.write_all()


def task4_url_redirection(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    response.status_code, response.reason = 302, 'Found'
    response.add_header('Location', f'http://{server.host}/data/index.html')
    response.write_all()


def task5_test_html(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    response.status_code, response.reason = 200, 'OK'
    with open("task5.html", "rb") as f:
        response.body = f.read()


def task5_cookie_login(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    obj = json.loads(request.read_message_body())
    if obj['username'] == 'admin' and obj['password'] == 'admin':
        response.status_code, response.reason = 200, 'OK'
        response.add_header('Set-Cookie', 'Authenticated=yes')
    else:
        response.status_code, response.reason = 403, 'Forbidden'


def task5_cookie_getimage(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    cookie_str = request.get_header('Cookie')
    if cookie_str:
        # a hack converting cookie string to dict
        cookie_str = cookie_str.replace('; ', '", "').replace('=', '": "')
        cookies = json.loads('{"' + cookie_str + '"}')
    else:
        cookies = {}

    if cookies.get('Authenticated') == 'yes':
        response.status_code, response.reason = 200, 'OK'
        path = 'data/test.jpg'  # assume file exists
        mimetype, _ = mimetypes.guess_type(path)
        if mimetype:
            response.add_header('Content-Type', mimetype)
        with open(path, "rb") as f:
            if request.method == 'GET':
                response.body = f.read()
            response.add_header('Content-Length', str(f.tell()))
    else:
        response.status_code, response.reason = 403, 'Forbidden'

    response.write_all()


def task5_session_login(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    obj = json.loads(request.read_message_body())
    if obj["username"] == 'admin' and obj['password'] == 'admin':
        response.status_code, response.reason = 200, 'OK'
        session_key = random_string()
        while session_key in server.session:
            session_key = random_string()
        server.session[session_key] = None
        response.add_header('Set-Cookie', f'SESSION_KEY={session_key}')
    else:
        response.status_code, response.reason = 403, 'Forbidden'

    response.write_all()


def task5_session_getimage(server: HTTPServer, request: HTTPRequest, response: HTTPResponse):
    cookie_str = request.get_header('Cookie')
    if cookie_str:
        # a hack converting cookie string to dict
        cookie_str = cookie_str.replace('; ', '", "').replace('=', '": "')
        cookies = json.loads('{"' + cookie_str + '"}')
    else:
        cookies = {}

    if cookies.get('SESSION_KEY') in server.session:
        from os.path import getsize
        response.status_code, response.reason = 200, 'OK'
        path = 'data/test.jpg'  # assume file exists
        mimetype, _ = mimetypes.guess_type(path)
        if mimetype:
            response.add_header('Content-Type', mimetype)
        response.add_header('Content-Length', str(getsize(path)))
        if request.method == 'GET':
            with open(path, "rb") as f:
                response.body = f.read()
    else:
        response.status_code, response.reason = 403, 'Forbidden'

    response.write_all()


YOUR_STUDENT_ID = 11912309

http_server = HTTPServer(config.LISTEN_PORT)
http_server.register_handler("/", default_handler)
# Register your handler here!
http_server.register_handler("/data", task2_data_handler, allowed_methods=['GET', 'HEAD'])
http_server.register_handler("/post", task3_json_handler, allowed_methods=['GET', 'HEAD', 'POST'])
http_server.register_handler("/redirect", task4_url_redirection, allowed_methods=['GET', 'HEAD'])
# Task 5: Cookie
http_server.register_handler("/api/login", task5_cookie_login, allowed_methods=['POST'])
http_server.register_handler("/api/getimage", task5_cookie_getimage, allowed_methods=['GET', 'HEAD'])
# Task 5: Session
http_server.register_handler("/apiv2/login", task5_session_login, allowed_methods=['POST'])
http_server.register_handler("/apiv2/getimage", task5_session_getimage, allowed_methods=['GET', 'HEAD'])

# Only for browser test
http_server.register_handler("/api/test", task5_test_html, allowed_methods=['GET'])
http_server.register_handler("/apiv2/test", task5_test_html, allowed_methods=['GET'])


def start_server():
    try:
        http_server.run()
    except Exception as e:
        http_server.listen_socket.close()
        print(e)


if __name__ == '__main__':
    start_server()
