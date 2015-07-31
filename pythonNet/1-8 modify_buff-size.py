#!/usr/bin/env python
# -*- coding: utf-8 -*-  
#This program is optimized for Python 2.7.

import socket

SEND_BUF_SIZE = 4096
RECV_BUF_SIZE = 4096

def modify_buff_size():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#Get the size of the socket's send buffer
	bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
	print "Buffer size [Before]:%d" % bufsize

	sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
	#SOL_SOCKET是正在使用的socket选项，使用无延迟发送，有数据就发
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF_SIZE)
	
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF_SIZE)

	bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
	print "Buffer size [Before]:%d" % bufsize

if __name__ == '__main__':
	modify_buff_size()