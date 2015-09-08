#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import socket
import threading
import SocketServer

SERVER_HOST = 'localhost'
SERVER_PORT = 0 #tells the kernel to pick up a port dynamically
BUF_SIZE = 1024
ECHO_MSG = 'Hello echo server!'

class ForkingClient():
    '''A client to test forking server'''
    def __init__(self, ip, port):
        #create a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #connect to the server
        self.sock.connect((ip, port))

    def run(self):
        '''client playing with server'''
        #send the data to server
        current_process_id = os.getpid()
        print "PID:%s sending echo message to the server:%s" % \
        	(current_process_id, ECHO_MSG)
        send_data_length = self.sock.send(ECHO_MSG)
        print "Sent:%d characters, so far..." % send_data_length

        #display server response
        response = self.sock.recv(BUF_SIZE)
        print "PID:%s received:%s" % (current_process_id, response)

    def shutdown(self):
    	self.sock.close()

class ForkingServerRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		#send the echo back to the client
		data = self.request.recv(BUF_SIZE)
		current_process_id = os.getpid()
		response = '%s: %s' % (current_process_id, data)
		print "Server sending response [current_process_id:data] = [%s]" %response
		self.request.send(response)
		return

class ForkingServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):#基于进程
	'''nothing to add here, inherited everything necessary from parents'''
	pass

def main():
	server = ForkingServer((SERVER_HOST,SERVER_PORT),ForkingServerRequestHandler)
	ip, port = server.server_address
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.setDaemon(True)
	server_thread.start()
	print "Server loop running PID:%s" % os.getpid()

	client1 = ForkingClient(ip, port)
	client1.run()

	client2 = ForkingClient(ip, port)
	client2.run()

	server.shutdown()
	client1.shutdown()
	client2.shutdown()
	server.socket.close()

if __name__ == '__main__':
    	main()    