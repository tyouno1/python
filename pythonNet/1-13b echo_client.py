#!/usr/bin/env python
#-*- coding:utf-8 -*-

import socket
import argparse

host = 'localhost'

def echo_client(port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print "Connect to %s port %s" % (host, port)
    sock.connect((host, port))

    try:
    	message = "Test message.This wil be echod"
    	sock.sendall(message)

    	amount_received =0
    	amount_expected = len(message)
    	while amount_received < amount_expected:
    		data = sock.recv(16)
    		amount_received += len(data)
    		print "Received:%s" % data
    except socket.errno, e:
    	print "Socket error:%s" % str(e)
    except socket.error, e:
    	print "Other exception:%s" % str(e)
    finally:
    	print "Closing connection to the server"
    	sock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Client Example')
    parser.add_argument('--port',help="input your port",action="store", dest="port", type=int, required=True)
    #required ：是否必选
    given_args = parser.parse_args()
    port = given_args.port

    echo_client(port) 