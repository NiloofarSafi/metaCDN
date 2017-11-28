from __future__ import division
import thread
import json
import requests
import shlex
import operator
import socket
import sys
import time
from subprocess import Popen, PIPE, STDOUT

#********* CONSTANT VARIABLES *********
BACKLOG = 50            # how many pending connections queue will hold
MAX_DATA_RECV = 4096    # max number of bytes we receive at once
DEBUG = False           # set to True to see the debug msgs

#********* MAIN PROGRAM ***************

def get_simple_cmd_output(cmd, stderr=STDOUT):

    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]

def get_ping_time(host):
    host = host.split(':')[0]
    cmd = "ping -c 1 " + host
    TTL = get_simple_cmd_output(cmd).strip().split(':')[-1].split()[1].split('=')[-1]
    RTT = get_simple_cmd_output(cmd).strip().split(':')[-1].split()[-2].split('/')[1]
    return TTL, RTT

def proxy(filename, flag, beta):
    print "inside proxy"

    host = '35.196.49.143' # for getting price info
    host2 = '35.196.49.143' # for getting server list

    port = 8700
    port2 = 8871

    # s = socket.socket()
    # s.connect((host, port))

    URL = 'http://' + host + ":" + str(port) + '/cost/get'
    URL2 = 'http://' + host2 + ":" + str(port2) + '/api/get'

    # print URL
    # print URL2

    req = requests.get(URL)
    # print "first request done!"
    req2 = requests.get(url = URL2)
    # print "second request done!"
    data = json.loads(req.content)
    data2 = json.loads(req2.content)

    price_dic = {}
    price_list = data['price']
    for option in price_list:
        price_dic[option['provider']] = option['server_hourly_cost']

    print 'data1: ', price_dic
    print 'data2: ', data2

    # print "I have data and data2!"

    if '.jpeg' in filename or '.jpg' in filename or '.png' in filename:
        URL3 = 'http://' + host2 + ":" + str(port2) + '/getrandom'
        prev = time.time()
        req3 = requests.get(url=URL3)
        print "REQ3 passed!"
        current = time.time()

        tt = current - prev
        URL3 = 'http://' + host2 + ":" + str(port2) + '/datarate?bandwidth=' + str(tt)
        req3 = requests.get(url=URL3)

    ttl = {}
    delays = {}
    price = {}

    ipdic = {}
    for key, val in data2.items():
        ipdic[val['ip_address']] = int(val['port'])

    print ipdic
    for key, val in price_dic.items():
        if key in data2:
            price[str(data2[key]['ip_address'])] = float(val)
            ip = str(data2[key]['ip_address'])
            if ip == "129.7.240.33":
                TTL = 59
                RTT = 0.274
            else:
                TTL, RTT = get_ping_time(ip)
            print ip, " ", TTL , " ", RTT
            #ttl[str(val['ip'])] = float(TTL)
            delays[ip] = float(RTT)

    # for key, val in data.items():
    # if key != 'Program':
    #     price[str(val['ip'])] = float(val['price'])
    #     ip = str(val['ip'])
    #     TTL, RTT = get_ping_time(ip)
    #     print ip, " ", TTL, " ", RTT
    #     ttl[str(val['ip'])] = float(TTL)
    #     delays[str(val['ip'])] = float(RTT)

    sorted_RTT = sorted(delays.items(), key=operator.itemgetter(1))
    sorted_TTL = sorted(ttl.items(), key=operator.itemgetter(1))
    sorted_price = sorted(price.items(), key=operator.itemgetter(1))

    # print sorted_RTT
    # print sorted_TTL
    if flag == 'p':
        return sorted_price[0][0], ipdic[sorted_price[0][0]]
    elif flag == 'n':
        return sorted_RTT[0][0], ipdic[sorted_RTT[0][0]]
    elif flag == 'c':
        combined = {}
        for key, val in price.items():
            combined[key] = beta*val + (1-beta)*delays[key]
        sorted_comb = sorted(combined.items(), key=operator.itemgetter(1))
        print sorted_comb
        return sorted_comb[0][0], ipdic[sorted_comb[0][0]]


def proxy_thread(conn, client_addr):

    request = conn.recv(MAX_DATA_RECV)

    first_line = request.split('\n')[0]
    print first_line
    url = first_line.split(' ')[1]
    print url
    required_fname = url.split('/')[-1]
    print required_fname
    #print 'system first argument is ', sys.argv[0], " ", type(sys.argv[0])
    # print 'system second argument is ', sys.argv[1], " ", type(sys.argv[1])
    if sys.argv[1] == 'c':
        #print('I am here')
        beta = float(sys.argv[2])
        #print 'I know beta is: ', beta
    else:
        beta = 0
    print "I am heading to proxy"
    print beta
    webserver, port = proxy(required_fname, sys.argv[1], beta)
    print "webserver: ", webserver
    print "port: ", port
    # print webserver
    # port = 22222

    print "Connect to:", webserver, port

    try:
        # create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        # print 'my request is: ', request
        s.send(request)         # send request to webserver

        while 1:
        # receive data from web server
            data = s.recv(MAX_DATA_RECV)

            if (len(data) > 0):
                # send to browser
                conn.send(data)
            else:
                break
        # print "I am closing the socket here!!!"
        s.close()
        conn.close()
    except socket.error, (value, message):
        # print "I am here because of bad request"
        if s:
            s.close()
        if conn:
            conn.close()
        print "Runtime Error:", message
        sys.exit(1)

def main():

    host = ''               # blank for localhost
    port = 8080

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(BACKLOG)
        # print "I am here"

    except socket.error, (value, message):
        # print("I am closing the connection")
        if s:
            s.close()
        print "Could not open socket:", message
        sys.exit(1)

    while 1:
        # print "Openning a new thread"
        conn, client_addr = s.accept()

        thread.start_new_thread(proxy_thread, (conn, client_addr))

    s.close()

if __name__ == '__main__':
    main()










# def get_simple_cmd_output(cmd, stderr=STDOUT):
#
#     args = shlex.split(cmd)
#     return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]
#
# def get_ping_time(host):
#     host = host.split(':')[0]
#     cmd = "ping -c 1 " + host
#     TTL = get_simple_cmd_output(cmd).strip().split(':')[-1].split()[1].split('=')[-1]
#     RTT = get_simple_cmd_output(cmd).strip().split(':')[-1].split()[-2].split('/')[1]
#     return TTL, RTT

# def proxy(flag, beta):
#     host = '35.196.127.69'
#     port = 3389
#     URL = 'http://' + host + ":" + str(port) + '/priceInf'
#
#     req = requests.get(url = URL)
#
#     data = json.loads(req.content)
#
#     ttl = {}
#     delays = {}
#     price = {}
#
#     for key, val in data.items():
#         price[str(val['ip'])] = float(val['price'])
#         ip = str(val['ip'])
#         TTL, RTT = get_ping_time(ip)
#         print ip, " ", TTL , " ", RTT
#         ttl[str(val['ip'])] = float(TTL)
#         delays[str(val['ip'])] = float(RTT)
#
#     sorted_RTT = sorted(delays.items(), key=operator.itemgetter(1))
#     sorted_TTL = sorted(ttl.items(), key=operator.itemgetter(1))
#     sorted_price = sorted(price.items(), key=operator.itemgetter(1))
#
#     # print sorted_RTT
#     # print sorted_TTL
#     if flag == 'p':
#         return sorted_price[0][0]
#     elif flag == 'n':
#         return sorted_RTT[0][0]
#     elif flag == 'c':
#         combined = {}
#         for key, val in price.items():
#             combined[key] = beta*val + (1-beta)*delays[key]
#         sorted_comb = sorted(combined.items(), key=operator.itemgetter(1))
#         return sorted_comb[0][0]
#
#
#     port = 8080
#     s = socket.socket()
#     s.bind(('127.0.0.1', port))
#     s.listen(5)
#     while(True):
#         c, addr = s.accept()  # Establish connection with client.
#         print 'Got connection from', addr
#         print "Receiving..."
#         request = c.recv(1024)
#         first_line = request.split('/n')[0]
#         url = first_line.split(' ')[1]
#         required_fname = url.split('/')[-1]
#         if sys.argv[0] == 'c':
#             beta = float(sys.argv[1])
#         else:
#             beta = 0
#         server_ip = proxy(sys.argv[0],beta)


