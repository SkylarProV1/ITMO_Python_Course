import time
import errno
import os
import signal
import socket
from io import StringIO
import sys
import serv
import logging



class AsyncWSGIServer(serv.AsyncServer):

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application


class AsyncWSGIRequestHandler(serv.AsyncHTTPRequestHandler):


    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version']      = b'1.0'
        env['wsgi.url_scheme']   = b'http'
        env['wsgi.input']        = "{self.request_data}".encode('utf-8')
        env['wsgi.errors']       = "{sys.stderr}".encode('utf-8')
        env['wsgi.multithread']  = "False".encode('utf-8')
        env['wsgi.multiprocess'] = "True".encode('utf-8')
        env['wsgi.run_once']     = "False".encode('utf-8')
        # Required CGI variables
        env['REQUEST_METHOD']    = "{self.request_method}".encode('utf-8')  # GET
        env['PATH_INFO']         = "{self.path}".encode('utf-8')             # /hello
        env['SERVER_NAME']       = "{self.server_name}".encode('utf-8')      # localhost
        env['SERVER_PORT']       = "{self.server_port}".encode('utf-8')  # 8888
        return env

    def start_response(self, status, response_headers, exc_info=None):
        weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
                weekdayname[wd],
                day, monthname[month], year,
                hh, mm, ss)
        # Add necessary server headers
        server_headers = [
            (b'Date', f"{s}".encode("utf-8")),
            (b'Server', b'WSGIServer 1.0'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip(b'\r\n')
        # Break down the request line into components
        (self.request_method,  # GET
         self.path,            # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()


    def handle_request(self):
        request_data = self.client_connection.recv(1024)
        self.request_data = request_data = request_data.decode('utf-8')
        # Print formatted request data a la 'curl -v'
        print(''.join(
            f'< {line}\n' for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = f"HTTP/1.1 {status}\r\n".encode('utf-8')
            for header in response_headers:
                response += f"{header[0]}: {header[1]}\r\n".encode("utf-8")
            response += b'\r\n'
            for data in result:
                response += data
            # Print formatted response data a la 'curl -v'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()

    def application(env, start_response):
        start_response(b'200 OK', [(b'Content-Type', b'text/plain')])
        return [b'Hello World']




SERVER_ADDRESS = (HOST, PORT) = '', 9000



if __name__=='__main__':
    log = logging.getLogger(__name__)
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    server = AsyncWSGIServer(log)
    server.set_app(application)
    #server.get_app()
    server.serve_forever()
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))

