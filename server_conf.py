"""simple HTTP server in python to provide an API for getting or updating the list of servers
Usage::
    python server_conf.py [port]
-- Please note that you can initialize your desired port as an input argument, but in this case you need to update
servers.json file and put that port as the port number for any of hosts (AWS, GC, Program) on which you are running the
code. If you don't want to initialize the port, you need to hard code it for each instance you run in different hosts as
the last argument of function "run"

Send a GET request::
    curl http://localhost:port/get/download

Send a POST request::
    curl -d "A=foo=bar&bin=baz" http://localhost:port/fname
    or
    curl http://localhost:port/api/set/fname?A=foo=bar-bin=baz
-fname is the name of file you are going to update
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import base64
import os
import sys
from PIL import Image
class S(BaseHTTPRequestHandler):
    def _set_headers(self, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    def do_GET(self):
        #print self.path
        if '/get/download' in self.path.lower():
            filename1 = self.path.split('/')[-1]
            ftype = filename1.split('.')[-1]
            fname = filename1.split('.')[0]
            if ftype == 'png' or ftype == 'jpeg':
                content_type = 'image/'+ftype
            elif ftype == 'jpg':
                content_type = 'image/jpeg'
            elif ftype == 'txt':
                content_type = 'text/html'
            self._set_headers(content_type)
            filename = './files/' + filename1
            if os.path.exists(filename):
                if ftype == 'png' or ftype == 'jpg' or ftype == 'jpeg':
                    if sys.argv[2] == 'static':
                        txtfile = open('bandwidth.txt', 'r').read()
                        bandwidth = float(txtfile)
                        if bandwidth < 10:
                            output = open(filename, 'rb').read()
                            self.wfile.write(output)
                        elif bandwidth > 10 and bandwidth < 100:
                            out_file = './files/' + fname + '_medium.' + ftype
                            output = open(out_file, 'rb').read()
                            self.wfile.write(output)
                        elif bandwidth > 100:
                            out_file = './files/' + fname + '_low.' + ftype
                            output = open(out_file, 'rb').read()
                            self.wfile.write(output)
                elif sys.argv[2] == "dynamic":
                    txtfile = open('bandwidth.txt', 'r').read()
                    bandwidth = float(txtfile)
                    if bandwidth < 10:
                        output = open(filename, 'rb').read()
                        self.wfile.write(output)
                    elif bandwidth > 10 and bandwidth < 100:
                        img = Image.open(filename)
                        output = img.resize([int(0.66 * s) for s in img.size])
                        output.save('./files/temp.jpg')
                        # out_file = './files/' + fname + '_medium.' + ftype
                        output = open('./files/temp.jpg', 'rb').read()
                        self.wfile.write(output)
                    elif bandwidth > 100:
                        # print "I am here!!!"
                        img = Image.open(filename)
                        output = img.resize([int(0.33 * s) for s in img.size])
                        output.save('./files/temp.jpg')
                        # print "I have the output"
                        output = open('./files/temp.jpg', 'rb').read()
                        # out_file = './files/' + fname + '_low.' + ftype
                        # output = open(out_file, 'rb').read()
                        self.wfile.write(output)
                        # print "I wrote the output"
                        # img = Image.open(filename)
                        # output = out1 = img.resize([int(first_version * s) for s in img.size])
                else:
                    output = open(filename, 'r').read()
                    # content = json.loads(output)['content']
                    # decoded_string = content.decode('base64')
                    self.wfile.write(output)
            else:
                self.wfile.write('BAD REQUEST: file does not exist!!')
                        #    if os.path.exists(filename):
                        #       output = open(filename, 'r').read()
                        # content = json.loads(output)['content']
                        # decoded_string = content.decode('base64')
                    #       self.wfile.write(output)
                    #    else:
                    #       self.wfile.write('BAD REQUEST: file does not exist!!')
        elif '/api/get' in self.path:
            self._set_headers('text/html')
            output = open('servers.json', 'r').read()
            self.wfile.write(output)
        elif '/getrandom' in self.path:
            self._set_headers('text/html')
            output = open('random_file.txt', 'r').read()
            self.wfile.write(output)
        elif '/datarate' in self.path:
            self._set_headers('text/html')
            cont = self.path.split('/')[-1]
            post_data = cont.split('?')[-1]
            bandwidth = post_data.split('=')[-1]
            with open('bandwidth.txt', 'w') as txtfile:
                txtfile.write(bandwidth)
            txtfile.close()
        elif '/api/set' in self.path:
            self._set_headers('text/html')
            # print "self.path: ", self.path
            cont = self.path.split('/')[-1]
            post_data = cont.split('?')[-1]
            fname = cont.split('?')[0]
            jfile = open(fname + '.json', 'r')
            jsfile = jfile.read()
            data = json.loads(jsfile)
            # print "post_data: ", post_data
            splitdata = post_data.split('-')
            first = splitdata[0].split('=')
            # print "first: ", first
            second = splitdata[1].split('=')
            # print "second: ", second
            for key, val in data.items():
                if key == first[0]:
                    dic = {}
                    dic[first[1]] = first[2]
                    dic[second[0]] = second[1]
                    data[key] = dic
            # self.wfile.write(data)
            jfile.close()
            with open(fname + '.json', 'w') as jsfile:
                json.dump(data, jsfile)
            # self.wfile.write(data)
            self.wfile.write({'status': 'posted!'})

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self._set_headers('text/html')
        fname = self.path.split('/')[-1]
        jfile = open(fname + '.json', 'r')
        jsfile = jfile.read()
        data = json.loads(jsfile)
        splitdata = post_data.split('&')
        first = splitdata[0].split('=')
        second = splitdata[1].split('=')
        for key, val in data.items():
            if key == first[0]:
                dic = {}
                dic[first[1]] = first[2]
                dic[second[0]] = second[1]
                data[key] = dic
                # self.wfile.write(data)
                jfile.close()
                with open(fname + '.json', 'w') as jsfile:
                    json.dump(data, jsfile)
                # self.wfile.write(data)
                self.wfile.write({'status': 'posted!'})

def run(server_class=HTTPServer, handler_class=S, port=8871):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()