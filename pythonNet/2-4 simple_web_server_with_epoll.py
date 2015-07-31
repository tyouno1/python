#!/usr/bin/env python
#-*- coding:utf-8 -*-

import socket
import select
import argparse

SERVER_HOST = 'localhost'

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
SERVER_RESPONSE = b"""HTTP/1.1 200 OK\r\nDate:Mon, 1 Apr 2013 01:01:01 GMT\r\nContent-Type:text/plain\r\nContent-Length: 25\r\n\r\nHello from Epoll Server!"""

class EpollServer(object):
    """ a socket server using epoll"""
    def __init__(self, host=SERVER_HOST, port=0):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#创建套接字
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#设置当前套接字选项为可重用
		self.sock.bind((host, port))#绑定
		self.sock.listen(1)#监听
		self.sock.setblocking(0)#设置套接字模式为非阻塞
		self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		#socket阻塞模式自动开启Nagle算法。设置套接字选项关闭。Nagle算法用于对缓冲区内的一定数量的消息进行自动连接。
		print "Started Epoll Server"
		self.epoll = select.epoll()#创建epoll对象
		self.epoll.register(self.sock.fileno(), select.EPOLLIN)
   		#为该socket的read event注册interest
   		#EPOLLIN表示对应的文件描述符可以读，包括对端SOCKET正常关闭
   		#fileno()返回的是该socket的一个整型文件描述符

    def run(self):
		"""Executes epoll server operation"""
		try:
			connections = {}	#连接对象与socket对象的映射
			requests = {}		
			responses = {}
			while True:
				events = self.epoll.poll(1)
				#查询epoll对象是否可能发生任何interest的事件。1等待一秒
				for fileno, event in events:#遍历事件
					#如果事件发生在服务器
					if fileno == self.sock.fileno():
						connection, address = self.sock.accept()#接收客户端socket和地址
						connection.setblocking(0)#设置非阻塞模式
						self.epoll.register(connection.fileno(), select.EPOLLIN)
						#为新的socket的read event注册兴趣					
						connections[connection.fileno()] = connection#添加到connections
						requests[connection.fileno()] = b''
						responses[connection.fileno()] = SERVER_RESPONSE#要发送的内容

					#如果一个读事件发生在客户端，那么读取从客户端发来的新数据
					elif event & select.EPOLLIN:
						requests[fileno] += connections[fileno].recv(1024)
						if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
							self.epoll.modify(fileno, select.EPOLLOUT)
		 	    			#注销对read event的interest，注册对write event的interest
		 	    			print('-'*40 + '\n' + requests[fileno].decode()[:-2])
							#输出完整的请求,去除最后一个\r\n

		 	    	#如果一个写事件发生在客户端，那么可能要接受来自客户端的新数据
					elif event & select.EPOLLOUT:
					#EPOLLOUT表示对应的文件描述符可以写
						byteswritten = connections[fileno].send(responses[fileno])
						responses[fileno] = responses[fileno][byteswritten:]
						if len(responses[fileno]) == 0:#如果无响应
							self.epoll.modify(fileno, 0)#禁用interest
			    			connections[fileno].shutdown(socket.SHUT_RDWR)
							#将对应的socket连接关闭

					#如果一个中止事件发生在客户端
					elif event & select.EPOLLHUP:
					#EPOLLHUP表示对应的文件描述符被挂断
						self.epoll.unregister(fileno)#注销客户端interest
						connections[fileno].close()#关闭socket连接
						del connections[fileno]#删除映射
		finally:
			self.epoll.unregister(self.sock.fileno())#注销服务器interest
			self.epoll.close()#关闭服务器epoll
			self.sock.close()#关闭服务器socket

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Server Example with Epoll')
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    server = EpollServer(host=SERVER_HOST, port=port)
    server.run()
