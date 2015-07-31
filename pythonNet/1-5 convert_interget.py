#!/usr/bin/env python
#This program is optimized for Python 2.7.

import socket

def convert_integer():
	data = 1234
	#32-bit
	print "Original:%s => Long host byte order:%s, Network byte order:%s" \
		%(data, socket.ntohl(data), socket.htonl(data))
	#16-bit
	print "Original:%s => short host byte order:%s, Network byte order:%s" \
		%(data, socket.ntohs(data), socket.htons(data))

if __name__ == '__main__':
	convert_integer()