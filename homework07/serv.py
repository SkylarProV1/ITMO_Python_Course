import asyncore
import asynchat
import socket
import multiprocessing
import logging
import mimetypes
import os
import urllib
from urllib.parse import urlparse
import argparse
from time import strftime, gmtime
import datetime
import time 
from email.parser import Parser
import cgi
from collections import deque
from urllib.parse import parse_qsl
from urllib.parse import urlparse


def url_normalize(path):
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1+3:]
        else:
            path = path.replace("/..", "", 1)
    path = path.replace("/./", "/")
    path = path.replace("/.", "")
    return path

FileSupport={'js':'text/javascript','html':'text/html',
    'css':'text/css','jpg':'image/jpeg','jpeg':'image/jpeg',
    'png':'image/png','gif':'image/gif'}

class FileProducer(object):

    def __init__(self, file, chunk_size=262144):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data and str(type(data)) != "<class 'bytes'>":
                return data.encode('utf-8')
            elif data:
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


    def handle_accepted(self,serversocket:socket.socket)-> None :
        while True: 
            clientsocket, (client_address, client_port) = self.serversocket.accept()
            self.log.warning(f"New client: {client_address}:{client_port}")
            try:
                AsyncHTTPRequestHandler(clientsocket=clientsocket,log=self.log)
                asyncore.loop()
            except Exception as e:
                print('Client serving failed', e)

    def serve_forever(self):

        self.log.warning(f"Starting Server at {self._host}:{self._port}")

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
        self.alldata=list() #save all data
        self.termval=list()
        self.head={
                'method':None ,
                'uri':None ,
                'protocol':None
                } #save head req
        self.body_req=list()# save body req
        self.simple='index.html'
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
        self.dir=os.getcwd()
        self.version="HTTP/1.1"
        self.set_terminator(b"\r\n\r\n")

    def collect_incoming_data(self,data):
        self.log.warning(f"Incoming data: {data}")
        self._collect_incoming_data(data)
        self.alldata.append(str(self._get_data(),'iso-8859-1'))


    def found_terminator(self):
        self.termval.append(self.get_terminator())
        self.parse_request()
    
    def parse_request(self):
        if None in list(self.dictheaders.values()):
            self.parse_headers()
            if None in list(self.dictheaders.values()):
                self.send_error(404,"Bad Request")
            if self.dictheaders.get('method')=='POST':
                if int(self.dictheaders.get('Content-Length')[0])>0:
                    self.set_terminator(int(self.dictheaders.get('Content-Length')[0]))
                else:
                    print(self.head)
                    print(self.body_req)
                    print(self.dictheaders)
                    self.handle_request()
            else:
                print(self.head)
                print(self.body_req)
                print(self.dictheaders)
                self.handle_request()
        else:
            self.parse_headers()
            print(self.body_req)
            print(self.dictheaders)
            self.handle_request()


    def parse_headers(self)->None:
        if len(self.alldata)==1 and None in list(self.dictheaders.values()):
            if len(self.alldata[0].split('\r\n')[0].split(' '))==3:
                head_req=self.alldata[0].split('\r\n')[0].split(' ')
                self.path=head_req[1]
                self.head['method'],self.head['uri'],self.head['protocol']=head_req[0],head_req[1],head_req[2]
            else:
                self.send_error(400)
            dreq=self.head 
            headers=self.alldata[0].split('\r\n')[1:]
            hdict = {h.split(':')[0]:[] for h in headers }
            for h in headers:
                k,v = h.split(':',1)
                hdict[k].append(v[1:])
            dreq.update(hdict)
            self.dictheaders=dreq
            return None
        if len(self.alldata)==2:
            self.body_req.append(self.alldata[1])
            return None

    def handle_request(self):
        method_name = 'do_' + self.dictheaders.get('method')
        if not hasattr(self, method_name):
            self.send_error(405)
            self.handle_close()
            return
        handler = getattr(self, method_name)
        handler()
        

    def send_header(self, keyword:str, value:str):
        self.push(f"{keyword}: {value}\r\n".encode('utf-8'))

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


    def send_response(self, code, message=None):
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        self.push(f"{self.version} {code} {message}\r\n".encode('utf-8'))
        self.send_header('Server', self.version)
        self.send_header('Date', self.date_time_string())

    def end_headers(self): 
        self.push(f"\r\n".encode('utf-8'))

    def date_time_string(self,timestamp=None):#no
        weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if timestamp is None:
            timestamp = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
                weekdayname[wd],
                day, monthname[month], year,
                hh, mm, ss)
        return s

    def send_head(self): 
        self.send_response(200)

    def translate_path(self,path):
        i=0
        temp1=''
        while '../' in path:
            if not '../' in  path[:i]:
                temp1+=path[i]
            if  '../' in  path[:i]:
                temp1=temp1[:len(temp1)-4]+url_normalize(path)
                break
            i+=1
        if temp1=='':
            parse=urlparse(path)
            path=parse.path
        else:
            parse=urlparse(temp1)
            path=parse.path

        query=parse.query
        query=parse_qsl(query,keep_blank_values=True)
        path=parse_qsl(path,keep_blank_values=True)[0][0]
        return (path,query)

    def ran_back(self):
        sevdir=os.getcwd()
        if os.getcwd()!=self.dir:
            for _ in range(len(sevdir.split('/'))-len(self.dir.split('/'))):
                os.chdir('../')

    def run_direct(self,paths):
        self.ran_back()
        try:
            paths=paths.split('/')[1:]
            for path in paths:
                if len(path.split('.'))==1:
                    os.chdir(path)
                else:
                    self.open_file=path 
        except Exception as e:
            self.ran_back()
            self.send_error(403)#ошибки
            self.handle_close()

    def do_GET(self):
        if self.path == '/':
            self.ran_back()
            try:
                self.send_head()
                f=open(self.simple)
                producer=FileProducer(f)
                producer=producer.more()
                self.send_header('Content-Length',len(producer))
                self.end_headers()
                self.push_with_producer(producer)
                self.handle_close()
            except Exception as e:
                self.ran_back()
                self.log.warning(f"DIRECT: {os.getcwd()}")
                print(e)
        else:
            self.ran_back()
            path,query=self.translate_path(path=self.path)
            self.run_direct(paths=path)
            try:
                f=open(self.open_file, 'rb')
                self.send_head()
                producer=FileProducer(f)
                producer=producer.more()
                self.send_header('Content-Length',len(producer))
                self.send_header('Content-Type',FileSupport.get(self.open_file.split('.')[1]))
                self.end_headers()
                for i in range(0,len(producer),65536):
                    self.push_with_producer(producer)
                self.handle_close()
                self.ran_back()
            except Exception as e:
                self.log.warning(f"DIRECT: {os.getcwd()}")
                self.ran_back()
                self.send_error(404)
                self.handle_close()

    def do_HEAD(self):
        if self.path == '/':
            self.ran_back()
            self.send_head()
            f=open(self.simple,'rb')
            producer=FileProducer(f)
            producer=producer.more()
            self.send_header('Content-Length',len(producer))
            self.end_headers()
            self.handle_close()
            self.ran_back()
        else:
            self.ran_back()
            path,query=self.translate_path(path=self.path)
            self.run_direct(paths=path)
            try:
                f=open(self.open_file, 'rb')
                self.send_head()
                producer=FileProducer(f)
                producer=producer.more()
                self.send_header('Content-Length',len(producer))
                self.send_header('Content-Type',FileSupport.get(self.open_file.split('.')[1]))
                self.end_headers()
                self.handle_close()
                self.ran_back()
            except Exception as e:
                self.send_error(404)
                self.handle_close()
                self.ran_back()

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