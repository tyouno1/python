#!/usr/bin/env python
#-*- coding:utf-8 -*-

import select 
import socket
import sys
import signal    #接收到信号就会打断原来的程序执行流程来处理信号
import cPickle   #进行python对象的序列
import struct    #计算数据大小
import argparse

SERVER_HOST = 'localhost'
CHAT_SERVER_NAME = 'server'

def send(channel, *args):
	buffer = cPickle.dumps(args)      #将python对象序列化保存到本地的文件
	value = socket.htonl(len(buffer))
	size = struct.pack("L", value)    #用于将Python的值根据格式转换字符串
	channel.send(size)
	channel.send(buffer)

def receive(channel):
	size = struct.calcsize("L")#用来计算特定格式的输出的大小，是几个字节
	size = channel.recv(size)
	try:
		size = socket.ntohl(struct.unpack("L", size)[0])
		#将字节流的字符串，转化成长整型
	except struct.error, e:
		return ''
	buf = ""
	while len(buf) < size:
		buf = channel.recv(size - len(buf))
	return cPickle.loads(buf)[0] #载入本地文件，恢复python对象

class ChatServer(object):
	'''an example chat server using select'''
	def __init__(self, port, backlog=5):
		self.clients = 0
		self.clientmap = {}
		self.outputs = []    #list output sockets
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((SERVER_HOST, port))
		print 'Server listening to port:%s...' % port
		self.server.listen(backlog)
		#cath keyboard interupts
		signal.signal(signal.SIGINT, self.sighandler)
		#检测到中断信号ctrl+c，就调用sighandler函数

	def sighandler(self, signum, frame):
		'''clean up client outputs '''
		#close the server
		print "shutting down server.."
		#close existing client sockets
		for output in self.outputs:
			output.close()
		self.server.close()

	def get_client_name(self, client):
		'''return the name of client'''
		info = self.clientmap[client]
		host, name = info[0][0], info[1]
		return '@'.join((name, host))

	def run(self):
		inputs = [self.server]
		self.outputs = []
		running = True
		while running:
			try:
				readable, writeable, exceptional = select.select(inputs, self.outputs, [])
			except select.error, e:
				break

			for sock in readable:
				if sock == self.server:
					#handle the server socket
					client, address = self.server.accept()
					print "chat server:got connection %d from %s" % (client.fileno(), address)

					#read the login name
					cname = receive(client).split('NAME: ')[1]

					#compute client name and send back
					self.clients += 1
					send(client, 'CLIENT: ' + str(address[0]))
					inputs.append(client)
					self.clientmap[client] = (address, cname)

					#send joining information to other clients
					msg = "\n(Connected:New client (%d) from %s)" % \
						(self.clients, self.get_client_name(client))
					for output in self.outputs:
						send(output, msg)
					self.outputs.append(client)
				elif sock == sys.stdin:
       				#handle standard input
       					junk = sys.stdin.readline()
       					running = False
				else:
					#handle all other sockets
       					try:
       						data = receive(sock)
       						if data:
       							#send as new client's message...
       							msg = '\n#[' + self.get_client_name(sock) + ']>>' + data
       							#send data to all except ourself
       							for output in self.outputs:
       								if output != sock:
       									send(output, msg)
       						else:
       								print "Chat Server:%d hung up" % sock.fileno()
                        			self.clients -= 1
                        			inputs.remove(sock)
                        			self.outputs.remove(sock)

									#sending client leaving information to others
                        			msg = "\n(Now hung up:Client from %s)" % self.get_client_name(sock)
                        			for output in self.outputs:
                        				send(output, msg)

                        			sock.close()
       					except socket.error, e:
       						#remove
       						inputs.remove(sock)
       						self.outputs.remove(sock)
		self.server.close() 
		
       	

class ChatClient(object):
	'''a command line chat client using select'''
	def __init__(self, name, port, host=SERVER_HOST):
		self.name = name
		self.connected = False
		self.host = host
		self.port = port
		#initial prompt
		self.prompt='['+'@'.join((name,socket.gethostname().split('.')[0]))+']>'
		#connect to server at port
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((host, self.port))
			print "Now connneted to char server@ port %d" % self.port
			self.connected = True
			#send my name..
			send(self.sock, 'NAME: ' + self.name)
			data = receive(self.sock)
			#contains client address, set it
			addr = data.split('CLIENT: ')[1]
			self.prompt = '[' + '@'.join((self.name, addr)) + ']>'
		except socket.error, e:
			print "Failed to connect to char server@ port %d" % self.port
			sys.exit(1)

	def run(self):
		'''chat client main loop'''
		while self.connected:
			try:
				sys.stdout.write(self.prompt)
				sys.stdout.flush()
				#wait for input from stdin and socket
				print "0"
				readable, writeable, exceptional = select.select(self.sock, [], [])
				print "1"
				for sock in readable:
					print "2"
					if sock == 0:
						data = sys.stdin.readline().strip()
						if data: send(self.sock, data)
					elif sock == self.sock:
							data = receive(self.sock)
							if not data:
								print "Client shutting down."
								self.connected = False
								break
							else:
								sys.stdout.write(data + '\n')
								sys.stdout.flush()
				print "3"
			except KeyboardInterrupt:
				print "Client interupted."
				self.sock.close()
				break

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Socket Server Example with Select')
	parser.add_argument('--name', action="store", dest="name", required=True)
	parser.add_argument('--port', action="store", dest="port", type=int, required=True)
	given_args = parser.parse_args()
	port = given_args.port
	name = given_args.name

	if name == CHAT_SERVER_NAME:
		server = ChatServer(port)
		server.run()
	else:
		client = ChatClient(name=name,port=port)
		client.run()