# project-milestone-2-NiloofarSafi

The goal of the project is to implement a metaCDN. Below, you can find the description for each python file:

- upload.py: It is a HTTP client implemented to upload an input file in an input server.

RUN: python upload.py [<file_path>] [<server_name>(AWS/GC/Program)] [<packet_format>(Json/Protobuf3)] 

Implementation details: This code reads the input file, convert it to json or Protobuf3 format using base64 encoding and send it to the server through a TCP protocol with openning the socket. It adds two fields as metadata to the json file: 1)the name of the file 2)a flag named distributed which is set to F (server.py use it to decide if distributed the uploaded file or not). The list of server ips and ports for connecting to server.py on each of service providers hardcoded in the code. In the case that the name of input server does not exist in the list it will return an error.  


- server.py: HTTP server to receive a file from upload.py, and distributes it to the other servers if "Distributed" flag is F (false).

RUN: python server.py [<resize(static/dynamic)>]

Implementation details: This code receives a file from client or another server and saves it in json format on the server. It also checks if it should distribute the file to the other servers that it knows (using server_list). Please note that we should run exactly the same instances of the code on each virtual machine, but we should hardcode the ports that we are going to use for running each instance. For using the same ports as we have on upload.py, you can open that file and see the port numbers in one of very first lines. You do not need to specify the hostname because it set to localhost.
Please note that every time that we stop and again start our instances on AWS and Google Cloud, both internal and external ips will be changed so we need to update them in the code.
In the second phase, server.py support SSL connection. It also has functionality to send and receive heartbeat messages.

- priceInfo.py: It provides an API to handle get and post requests regarding to know or update the price for each server using the information in priceInf.json. The details how it can be run, were provided above the code. Please note that it is possible to initialize an arbitrary port as an input argument for this code. But, we do need to update the port number we want to use to connect from proxy.py to this server in proxy.py (variable "port")  

- server_conf.py: It provides an API to handle get and post requests regarding to know or update the server list using the information in servers.json. It also provide an API for user through proxy.py to download the desired files if they exist on the server. The details how it can be run, were provided above the code. Please note that it is possible to initialize an arbitrary port as an input argument for this code. But, we do need to update the port number in servers.py (we can do it by sending a post request to servers.json through the same code) 

RUN: server_conf [<resize(static/dynamic)>]

- proxy.py: This is a HTTP proxy server that calculates which server is better for downloading the required file. It gets two input arguments in command line: 1) one of letters among "p" (price), "n" (network), "c" (combination) to choose the method for performance measurements 2) beta which should be a number between 0 and 1 that specifies how it should combine the network and price information to make routing path. if the first argument is not "c", beta will be set to 0.
proxy send requests to both priceInfo.py for knowing the prices, and server_conf.py to knowing the list of all servers. Then, computes which server has the better performance and send a request to server_conf.py running on that server to download the required file. 

RUN: python proxy [c/p/d] [beta]

The following json files were also uploaded:

- server_list_[AWS/GC/Program].json: These files contain the list of other servers, and the ports the server can use to
connect to them by server.py (for distributing the uploaded file).

- servers.json: This file contains the name of all servers with the ports that proxy may use to connect to server_conf.py
on each of servers. This file can be read or updated by server_conf API.

- priceInf.json: This file contains the price for each server. It can be read or updated through priceInfo API.

Also you can find the certificate and key files we use for SSL connection.

## Reference:
- For implementing HTTP server and client I changed and customized the codes in this link: https://stackoverflow.com/questions/27241804/sending-a-file-over-tcp-sockets-in-python
- For implementing APIs (priceInfo.py and server_conf.py) I changed and customized the codes in this link: https://gist.github.com/bradmontgomery/2219997
- For implementing proxy.py I changed and customized the codes in this link: http://luugiathuy.com/2011/03/simple-web-proxy-python/

