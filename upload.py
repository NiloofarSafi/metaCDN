import socket
import json
import sys
import base64
import packet_pb2
import ssl

server_dic = {'AWS':{ "ip": "54.152.56.65", "port": 3389 }, 'GC': { "ip": "35.196.49.143", "port": 3389 }, 'Program': { "ip": "129.7.240.33", "port": 22222 }}

server_name = sys.argv[2]
file_path = sys.argv[1]
encoding_flag = sys.argv[3]

file = open(file_path, 'rb')
content = file.read()
file.close()

encoded_content = base64.b64encode(content)

if "/" in file_path:
    fname = file_path.split("/")[-1]
else:
    fname = file_path

if encoding_flag == "json":
    print "Using json to upload data to the server!"
    json_content = {}
    json_content['file_name'] = fname
    json_content['distributed'] = 'T'
    json_content['content'] = encoded_content
    json_format = json.dumps(json_content)
    print 'size of json: ', sys.getsizeof(json_format)

elif encoding_flag == "protobuf3":
    packet = packet_pb2.Pack()
    packet.file_name = fname
    packet.content = encoded_content
    packet.distributed = 'T'
    print 'size of protobuf: ', packet.ByteSize()

host = ''
port = ''

s = socket.socket()         # Create a socket object
ssl_s= ssl.wrap_socket(s,ca_certs= "apache-selfsigned.crt",cert_reqs=ssl.CERT_REQUIRED)

for key, val in server_dic.items():
    if key == server_name:
        host = val['ip']      # Get local machine name
        port = val['port']    # Reserve a port for your service.

# print "host: ", host
# print "port: ", port

if host == '':
    print('Host name is invalid. Please choose one from (AWS/GC/Program)')
    sys.exit()

ssl_s.connect((host, port))
print 'Sending...'
# l = f.read(1024)
# while (l):
#     print 'Sending...'
if encoding_flag == 'json':
    # print json_format
    ssl_s.sendall(json_format)
elif encoding_flag == 'protobuf3':
    # print(packet.SerializeToString())
    ssl_s.sendall(packet.SerializeToString())
    # l = f.read(1024)

print "Done Sending"
ssl_s.shutdown(socket.SHUT_WR)
# print ssl_s.recv(1024)
ssl_s.close()