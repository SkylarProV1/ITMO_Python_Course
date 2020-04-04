import asyncore
import asynchat
import socket
import multiprocessing
import logging
import mimetypes
import os
#from urlparse import parse_qs
import urllib
import argparse
from time import strftime, gmtime
import datetime
import time 
from email.parser import Parser


def url_normalize(path):
    if path.startswith("."):
        path = "/" + path
        while "../" in path:
            p1 = path.find("/..")
            p2 = path.rfind("/", 0, p1)
            if p2 !=-1:
                path = path[:p2] + path[p1+3:]
            else:
                path = path.replace("/..", "", 1)
                path = path.replace("/./", "/")
                path = path.replace("/.", "")
        return path


class FileProducer(object):


    def __init__(self, file, chunk_size=4096):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data:
                return data
            self.file.close()
            self.file = None
        return ""

class AsyncServer(asyncore.dispatcher):


    def __init__(self,log, host="127.0.0.1", port=9000):
        self._host = host
        self._port = port
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.serversocket.bind((self._host,self._port))
        self.serversocket.listen(128)
        self.log=log


    def handle_accepted(self,serversocket:socket.socket,)-> None :
        while True: 
            clientsocket, (client_address, client_port) = self.serversocket.accept()
            self.log.warning(f"New client: {client_address}:{client_port}")
            try:
                AsyncHTTPRequestHandler(clientsocket=clientsocket,log=self.log)
                asyncore.loop()
            except Exception as e:
                print('Client serving failed', e)

    def serve_forever(self):

        print(f"Starting Server at {self._host}:{self._port}")

        NUMBER_OF_PROCESS = multiprocessing.cpu_count()
        processes = []
        self.log.warning(f"Number of processes: {NUMBER_OF_PROCESS}")
        for _ in range(NUMBER_OF_PROCESS):
            process = multiprocessing.Process(target=self.handle_accepted,
                args=(self.serversocket,))
            process.start()
            processes.append(process)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            for p in processes:
                p.terminate()
            self.serversocket.close()
 
class AsyncHTTPRequestHandler(asynchat.async_chat):


    def __init__(self,clientsocket,log):
        super().__init__(clientsocket)
        self.head=list()
        self.body_req=list()
        self.dictheaders={
                'method':None ,
                'uri':None ,
                'protocol':None ,
                'Host':None ,
                'User-Agent':None ,
                'Accept':None
                }
        self.log=log
        self.clientsocket=clientsocket
        self.set_terminator(b"\r\n\r\n")

    def collect_incoming_data(self,data):
        self.data=data
        self.log.warning(f"Incoming data: {data}")
        self._collect_incoming_data(self.data)

    def found_terminator(self):
        self.parse_request(self)
    
    def parse_request(self,data):
        if None in list(self.dictheaders.values()):
            self.dictheaders=self.parse_headers(self)
            if None in list(self.dictheaders.values()):
                self.log.error(f"400 Bad Request: {self.dictheaders}")
            if self.dictheaders.get('method')=='POST':
                if int(self.dictheaders.get('Content-Length')[0])>0:
                    self.set_terminator(int(self.dictheaders.get('Content-Length')[0]))
                else:
                    print(self.body_req)
                    print(self.dictheaders)
                    self.handle_request()
            else:
                print(self.body_req)
                print(self.dictheaders)
                self.handle_request()            
        else:
            try:
                self.body_req.append(self.data)
                self._collect_incoming_data(self.data)
                print(self.body_req)
                print(self.dictheaders)
                self.handle_request()
            except Exception as e:
                print(e)

    def parse_headers(self,data):
        self.head.append(self.data)
        self._collect_incoming_data(self.data)
        self.req_line= str(self.head[0], 'iso-8859-1').split('\r\n')[0].split()
        if len(self.req_line) !=3:
            raise Exception('Malformed request line')
        dreq={'method':self.req_line[0],'uri':self.req_line[1],'protocol':self.req_line[2]}
        headers=str(self.head[0], 'iso-8859-1').split('\r\n')[1:]
        hdict = {h.split(':')[0]:[] for h in headers }
        for h in headers:
            k,v = h.split(':',1)
            hdict[k].append(v[1:])
        dreq.update(hdict)
        return dreq
        

    def handle_request(self):
        method_name = 'do_' + self.dictheaders.get('method')
        if not hasattr(self, method_name):
            self.send_error(405)
            self.handle_close()
            return
        handler = getattr(self, method_name)
        handler()

    def send_header(self, keyword, value):
        sent_message='{}: {} \n'.format(str(keyword),value)
        sent_message=sent_message.encode('utf-8')
        while True:
            sent_len = self.clientsocket.send(sent_message)
            if sent_len == len(sent_message):
                break 
            sent_message = sent_message[sent_len:]
        return None

    def send_error(self, code, message=None):
        try:
            short_msg, long_msg = self.responses[code]
        except KeyError:
            hort_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg

        self.send_response(code, message)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()

    def send_response(self, code, message=None)->None : #ERROR
        sent_message='ERROR {}: {} {} \n'.format(str(code),message,self.date_time_string())
        sent_message=sent_message.encode('utf-8')
        while True:
            sent_len = self.clientsocket.send(sent_message)
            if sent_len == len(sent_message):
                break 
            sent_message = sent_message[sent_len:]
        return None

    def end_headers(self)->None: #ERROR
        sent_message=''
        sent_message=sent_message.encode('utf-8')
        while True:
            sent_len = self.clientsocket.send(sent_message)
            if sent_len == len(sent_message):
                break 
            sent_message = sent_message[sent_len:]
        return None

    def date_time_string(self):#no
        return time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())

    def send_head(self)->None: 
        sent_message='Method: {} | Uri: {} | Protocol: {}'.format(self.req_line[0],self.req_line[1],self.req_line[2])
        sent_message=sent_message.encode('utf-8')
        while True:
            sent_len = self.clientsocket.send(sent_message)
            if sent_len == len(sent_message):
                break
            sent_message = sent_message[sent_len:]

    def translate_path(self, path): 
        pass

    def do_GET(self)->None:# curl -d "key1=value1&key2=value2" "127.0.0.1:9000"
        while True:
            self.send_head()
            


    def do_HEAD(self):#no curl -i "key1=value1&key2=value2" "127.0.0.1:9000"
        pass

    responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        400: ('Bad Request',
            'Bad request syntax or unsupported method'),
        403: ('Forbidden',
            'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
            'Specified method is invalid for this resource.'),
    }


def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    parser.add_argument("--log", dest="loglevel", default="info")
    parser.add_argument("--logfile", dest="logfile", default=None)
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()


def run(args,log):
    server = AsyncServer(log=log,host=args.host,port=args.port)
    server.serve_forever()


if __name__ == "__main__":
    args = parse_args()


    logging.basicConfig(
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__)

    DOCUMENT_ROOT = args.document_root
    for _ in range(args.nworkers):
        p = multiprocessing.Process(target=run(args,log))
        p.start()