import threading
import socket  # Import socket module
import json
import os
import sys
from threading import Thread, current_thread
from PIL import Image
import base64
import time
import packet_pb2
from google.protobuf.json_format import MessageToJson

import ssl


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            conn = ssl.wrap_socket(client, server_side=True, certfile="apache-selfsigned.crt",
                                         keyfile="apache-selfsigned.key")

            conn.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(conn, address)).start()

    def listenToClient(self, conn, address):
        json_flag = False
        thread_name = threading.current_thread().getName()
        id = thread_name.split('-')[-1]
        # print thread_name
        # print id
        f_name = 'new_file_' + id + '.json'
        f = open(f_name, 'wb')
        print "open file: ", f_name
        while True:
            try:
                print 'Got connection from', address
                print "Receiving..."
                l = conn.recv(1024)
                while (l):
                    f.write(l)
                    l = conn.recv(1024)

            except:
                conn.close()
                return False

            f.close()
            print "Done recieving data"
            conn.close()
            json_file = open(f_name)
            content = json_file.read()
            # print(content)
            if content[0] == '{':
                print "Recieved json file"
                json_flag = True
                data = json.loads(content)
            else:
                print "Recieved protobuf3"
                json_flag = False
                packet = packet_pb2.Pack()
                packet.ParseFromString(content)
            json_file.close()
            if json_flag:
                data_fname = data['file_name']
                if data_fname == 'heartbeat':
                    print "heartbeat recieved from", data["ip_address"]
                    server_name = data['name']
                    with open("server_list.json", 'r') as serverfile:
                        servers = json.load(serverfile)
                    serverfile.close()
                    #current = time.time()
                    if server_name in servers:
                        added_server = False
                        servers[server_name]['last_live'] = time.time()

                        for key, val in servers.items():
                            if (time.time() - val["last_live"] > 2 * recv_heartbeat_timeout):
                                print "server ", key, " deleted!"
                                del servers[key]

                    else:
                        added_server = True
                        server_info = {}
                        server_info["ip_address"] = data["ip_address"]
                        server_info['port'] = data['port']
                        server_info['last_live'] = time.time()
                        servers[server_name] = server_info
                        for key,val in servers.items():
                            if(time.time() - val["last_live"] > 2 * recv_heartbeat_timeout):
                                print "server ", key, " deleted!"
                                del servers[key]

                    with open("server_list.json", 'w') as serverfile:
                        json.dump(servers, serverfile)
                    serverfile.close()

                    if added_server:
                        print "Distributing files to the new server ..."
                        path = './files/'
                        for files in os.listdir(path):
                            f = open(path+files, 'rb')
                            contents = f.read()
                            f.close()
                            json_content = {}
                            econded = base64.b64encode(contents)
                            json_content['file_name'] = files
                            json_content['content'] = econded
                            json_content['distributed'] = 'T'
                            jsonfile = json.dumps(json_content)
                            s2 = socket.socket()
                            host2 = server_info["ip_address"]
                            port2 = server_info['port']
                            ssl_s2 = ssl.wrap_socket(s2, ca_certs="apache-selfsigned.crt",
                                                       cert_reqs=ssl.CERT_REQUIRED)
                            ssl_s2.connect((host2, port2))
                            print 'Sending.. to new server added.'
                            ssl_s2.sendall(jsonfile)
                            print "Done Sending to new server added"
                            ssl_s2.shutdown(socket.SHUT_WR)
                            ssl_s2.close()
                            added_server = False

                else:
                    if data['distributed'] == 'F':
                        data['distributed'] = 'T'
                        with open("server_list.json") as serverfile:
                            servers = json.load(serverfile)
                        serverfile.close()
                        json_content = json.dumps(data)

                        for k, val in servers.items():
                            # print k, ' ', v
                            host1 = val['ip_address']
                            port1 = val['port']
                            s1 = socket.socket()  # Create a socket object
                            ssl_s1 = ssl.wrap_socket(s1, ca_certs="apache-selfsigned.crt",
                                                       cert_reqs=ssl.CERT_REQUIRED)
                            ssl_s1.connect((host1, port1))
                            # Reserve a port for your service.
                            print 'Distributing to ', host1
                            ssl_s1.sendall(json_content)
                            print "Done distributing!"
                            ssl_s1.shutdown(socket.SHUT_WR)
                            ssl_s1.close()

                    # filename = data['filename'].split('.')[0] + '.json'
                    fname = data['file_name']
                    path = './files/' + fname
                    content = base64.b64decode(data['content']) #actual data
                    with open(path, 'w') as outfile:
                        outfile.write(content)
                    outfile.close()

                    if (sys.argv[1] == 'static'):
                        if ".jpeg" in fname or ".jpg" in fname or "png" in fname:
                            print "Resizing the image"
                            img = Image.open(path)
                            first_version = 0.33
                            second_version = 0.66
                            out1 = img.resize([int(first_version * s) for s in img.size])
                            out2 = img.resize([int(second_version * s) for s in img.size])
                            f = fname.split('.')
                            file1 = './files/' + f[0] + '_low.' + f[-1]
                            out1.save(file1)
                            file2 = './files/' + f[0] + '_medium.' + f[-1]
                            out2.save(file2)
                            print "Resized images saved!"

                os.remove(f_name)

            elif not json_flag:
                json_conversion = MessageToJson(packet)
                print "Now the type of message is protobuf!"

                if packet.distributed == 'F':
                    packet.distributed = 'T'
                    with open("server_list.json") as serverfile:
                        servers = json.load(serverfile)
                    serverfile.close()
                    protobuf_content = packet.SerializeToString()
                    for k, val in servers.items():
                        s1 = socket.socket()  # Create a socket object
                        host1 = val['ip_address']
                        port1 = val['port']
                        ssl_s1 = ssl.wrap_socket(s1, ca_certs="apache-selfsigned.crt", cert_reqs=ssl.CERT_REQUIRED)
                        ssl_s1.connect((host1, port1))
                        # Reserve a port for your service.
                        print 'Distributing to ', host1
                        ssl_s1.sendall(protobuf_content)
                        print "Done Sending"
                        ssl_s1.shutdown(socket.SHUT_WR)
                        ssl_s1.close()

                fname = packet.file_name
                path = './files/' + fname
                output = base64.b64decode(packet.content)
                with open(path, 'w') as outfile:
                    outfile.write(output)
                outfile.close()

                if sys.argv[1] == 'static':
                    if ".jpeg" in fname or ".jpg" in fname or "png" in fname:
                        print "Resizing the image"
                        img = Image.open(path)
                        first_version = 0.33
                        second_version = 0.66
                        out1 = img.resize([int(first_version * s) for s in img.size])
                        out2 = img.resize([int(second_version * s) for s in img.size])
                        f = fname.split('.')
                        file1 = './files/' + f[0] + '_low.' + f[-1]
                        out1.save(file1)
                        file2 = './files/' + f[0] + '_medium.' + f[-1]
                        out2.save(file2)
                        print "Resized images saved!"

                os.remove(f_name)




if __name__ == "__main__":
    send_heartbeat_timeout = 40
    recv_heartbeat_timeout = 80
    # host = socket.gethostname()  # Get local machine name
    port = 22222
    # heartbeat_message = {}
    # heartbeat_message['message'] = 'I am alive'
    # heartbeat_message['name'] = 'Program'
    # heartbeat_message['ip_address'] = host
    # heartbeat_message['port'] = port
    # heartbeat_json_format = json.dumps(heartbeat_message)
    # port_num = input("Port? ")
    # try:
    #     port_num = int(port_num)
    #     break
    # except ValueError:
    #     pass
    # ThreadedServer('',port_num).listen()
    start = time.time()
    threading.Thread(target=ThreadedServer('', port).listen).start()
    last_heartbeat = start
    while True:
        # send heartbeat to every one
        if time.time() - last_heartbeat > send_heartbeat_timeout:
            with open("server_list.json") as serverfile:
                servers = json.load(serverfile)
            serverfile.close()
            for k, val in servers.items():
                host1 = val['ip_address']
                port1 = val['port']
                ss = socket.socket()  # Create a socket object
                ssl_ss = ssl.wrap_socket(ss, ca_certs="apache-selfsigned.crt", cert_reqs=ssl.CERT_REQUIRED)
                ssl_ss.connect((host1, port1))
                print 'Sending Heartbeat ...'
                heartbeat_content = open('heartbeat.json').read()
                ssl_ss.sendall(heartbeat_content)
                print "Done sending heartbeat"
                ssl_ss.shutdown(socket.SHUT_WR)
                ssl_ss.close()
                last_heartbeat = time.time()

                """
                        start = time.time()
                        with open('server_list.json', 'r') as jsonfile:
                            serverlist = json.load(jsonfile)
                        jsonfile.close()
                        for server, info in serverlist.items():
                            if start - info['last_live'] > recv_heartbeat_timeout:
                                 del serverlist[server]
                        with open('server_list.json', 'w') as jsonfile:
                            json.dump(serverlist, jsonfile)
                        jsonfile.close()"""








