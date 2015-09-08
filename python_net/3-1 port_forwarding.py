#!/usr/bin/env python
#-*- coding:utf-8 -*-

import argparse
import asyncore
import socket

LOCAL_SERVER_HOST = 'localhost'
REMOTE_SERVER_HOST = 'www.baidu.com'
BUFSIZE = 4096
LOCAL_SERVER_PORT = 0

class PortForwarder(asyncore.dispatcher):#监听本地
	def __init__(self, ip, port, remoteip, remoteport, backlog=5):
		asyncore.dispatcher.__init__(self)
		self.remoteip = remoteip
		self.remoteport = remoteport
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)#创建一个套接字对象
		self.set_reuse_addr()#设置地址端口可重用
		self.bind((ip, port))#绑定本地ip与端口
		self.listen(backlog)#开始监听

	def handle_accept(self):#处理接受
		conn, addr = self.accept()#等待接受
		print "Connected to:", addr
		Sender(Receiver(conn), self.remoteip, self.remoteport)

class Receiver(asyncore.dispatcher):#接受本地请求数据，发送给远程主机
	def __init__(self, conn):
		asyncore.dispatcher.__init__(self, conn)
		#self被初始化为该连接客户端socket
		#getpeername函数用于获取与某个套接字关联的外地协议地址 
		self.from_remote_buffer = ''#保存来自远程主机数据
		self.to_remote_buffer = ''	#保存本地请求数据
		self.sender = None

	def handle_connect(self):
		pass

	def handle_read(self):#接受本地请求
		read = self.recv(BUFSIZE)
		self.to_remote_buffer += read;
		print "receiver read", self.to_remote_buffer

	def writable(self):#判断是否有来自远程主机的数据，如果有，调用handle_write
		return (len(self.from_remote_buffer) > 0)

	def handle_write(self):#发送来自远程主机的数据给本地主机
		sent = self.send(self.from_remote_buffer)
		print "receiver sent", sent
		self.from_remote_buffer = self.from_remote_buffer[sent:]#发送完成后清空数据

	def handle_close(self):
		self.close()
		if self.sender:
			self.sender.close()

class Sender(asyncore.dispatcher):#接受远程主机数据，发送本地请求数据
	def __init__(self, receiver, remoteaddr, remoteport):
		asyncore.dispatcher.__init__(self)
		self.receiver = receiver#建立Sender与Receiver之间联系
		receiver.sender = self	#建立Sender与Receiver之间联系
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)#创建套接字
		self.connect((remoteaddr, remoteport))#连接远程主机

	def handle_connect(self):
		pass

	def handle_read(self):#接受来自远程主机的数据
		read = self.recv(BUFSIZE)
		self.receiver.from_remote_buffer += read
		print "sender read", self.receiver.from_remote_buffer

	def writable(self):#判断是否有本地请求要发送，如果有，调用handle_write
		if len(self.receiver.to_remote_buffer) > 0:
			self.receiver.to_remote_buffer = self.receiver.to_remote_buffer.replace\
				(LOCAL_SERVER_HOST + ':' + str(LOCAL_SERVER_PORT), REMOTE_SERVER_HOST)
			#在windows下运行需要这个if语句
			#如果有本地请求要发送，将本地主机中host改为远程主机地址
		return (len(self.receiver.to_remote_buffer) > 0)

	def handle_write(self):#发送本地请求数据
		sent = self.send(self.receiver.to_remote_buffer)
		print "sender write",sent
		self.receiver.to_remote_buffer = self.receiver.to_remote_buffer[sent:]

	def handle_close(self):
		self.close()
		self.receiver.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="stackless socket server example")
	parser.add_argument('--localhost', action="store", dest="local_host", default=LOCAL_SERVER_HOST)
	parser.add_argument('--local-port', action="store", dest="local_port", type=int, required=True)
	parser.add_argument('--romote-port', action="store", dest="remote_host",default=REMOTE_SERVER_HOST)
	parser.add_argument('--remot-port', action="store", dest="remote_port", type=int, default=80)
	given_args = parser.parse_args()
	local_host, remote_host = given_args.local_host, given_args.remote_host
	local_port, remote_port = given_args.local_port, given_args.remote_port
	LOCAL_SERVER_PORT = local_port
	print "start port forwarding local %s:%s => remote %s:%s" % \
		(local_host, local_port, remote_host, remote_port)
	PortForwarder(local_host, local_port, remote_host, remote_port)
	asyncore.loop()
