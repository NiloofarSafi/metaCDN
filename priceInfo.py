"""simple HTTP server in python to provide an API for getting or updating the price for each server
Usage::
    python priceInfo.py [port]
-- Please note that you can initialize your desired port as an input argument, but in this case you need to update
servers.json file and put that port as the port number for any of hosts (AWS, GC, Program) on which you are running the
code. If you don't want to initialize the port, you need to hard code it for each instance you run in different hosts as
the last argument of function "run"

Send a GET request::
    curl http://localhost:port/cost/get

Send a POST request::
    curl -d "A=foo=bar&bin=baz" http://localhost:port/cost/post
    or
    curl http://localhost:port/cost/post/fname?A=foo=bar-bin=baz
-fname is the name of file you are going to update
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import base64
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        self._set_headers()
        if '/cost/get' in self.path:
            output = open('priceInf.json', 'r').read()
            self.wfile.write(output)
        elif '/cost/post' in self.path:
            #print "self.path: ", self.path
            cont = self.path.split('/')[-1]
            post_data = cont.split('?')[-1]
            provider = cont.split('?')[0]
            fname = 'priceInf.json'
            jfile = open(fname, 'r')
            jsfile = jfile.read()
            data = json.loads(jsfile)
            #print "post_data: ", post_data
            splitdata = post_data.split('&')
            first = splitdata[0].split('=')
            #print "first: ", first
            second = splitdata[1].split('=')
            #print "second: ", second
            for option in data['price']:
                if option['provider'] == provider:
                    option[first[0]] = first[1]
                    option[second[0]] = second[1]
                    #dic ={}
                    #dic[first[1]] = first[2]
                    #dic[second[0]] = second[1]
                    #data[key] = dic
            #self.wfile.write(data)
            jfile.close()
            with open(fname,'w') as jsfile:
                json.dump(data, jsfile)
            self.wfile.write(data)
            # self.wfile.write({'status': 'posted!'})
        elif '/addcost' in self.path:
            cont = self.path.split('/')[-1]
            post_data = cont.split('?')[-1]
            provider = cont.split('?')[0]
            fname = 'priceInf.json'
            jfile = open(fname, 'r')
            jsfile = jfile.read()
            data = json.loads(jsfile)
            # print "post_data: ", post_data
            splitdata = post_data.split('&')
            first = splitdata[0].split('=')
            # print "first: ", first
            second = splitdata[1].split('=')
            # print "second: ", second
            jfile.close()
            price_list = data['price']
            dic = {}
            dic[first[0]] = first[1]
            dic['provider'] = provider
            dic[second[0]] = second[1]
            price_list.append(dic)
            data['price'] = price_list
            with open(fname, 'w') as jsfile:
                json.dump(data, jsfile)
            self.wfile.write(data)
            # self.wfile.write({'status': 'posted!'})
        elif '/cost/delete' in self.path:
            provider = self.path.split('/')[-1]
            fname = 'priceInf.json'
            jfile = open(fname, 'r')
            jsfile = jfile.read()
            data = json.loads(jsfile)
            jfile.close()
            price_list = data['price']
            new_list = []
            for option in price_list:
                if option['provider'] != provider:
                    new_list.append(option)
            data['price'] = new_list
            with open(fname, 'w') as jsfile:
                json.dump(data, jsfile)
            self.wfile.write(data)

        def do_POST(self):
            self._set_headers()
            if '/cost/post' in self.path:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                self._set_headers()
                fname = 'priceInf.json'
                jfile = open(fname, 'r')
                jsfile = jfile.read()
                data = json.loads(jsfile)
                jfile.close()
                splitdata = post_data.split('&')
                first = splitdata[0].split('=')
                second = splitdata[1].split('=')
                third = splitdata[2].split('=')
                for option in data['price']:
                    if option['provider'] == second[1]:
                        option[first[0]] = first[1]
                        option[third[0]] = third[1]
                # self.wfile.write(data)
                with open(fname, 'w') as jsfile:
                    json.dump(data, jsfile)
                self.wfile.write(data)
                # self.wfile.write({'status': 'posted!'})

            elif 'cost/delete' in self.path:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                self._set_headers()
                provider = self.path.split('/')[-1]
                jfile = open('priceInf.json', 'r')
                jsfile = jfile.read()
                data = json.loads(jsfile)
                # splitdata = post_data.split('&')
                # first = splitdata[0].split('=')
                # second = splitdata[1].split('=')
                server_name = post_data
                jfile.close()
                server_list = data['price']
                new_list = []
                for option in server_list:
                    if option['provider'] != server_name:
                        new_list.append(option)
                data['price'] = new_list
                with open('priceInf.json', 'w') as jsfile:
                    json.dump(data, jsfile)
                self.wfile.write(data)
                # self.wfile.write({'status': 'posted!'})

def run(server_class=HTTPServer, handler_class=S, port=8700):
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