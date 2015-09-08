#!/usr/bin/env python
#This program is optimized for Python 2.7.

import socket

def find_service_name():
	protocolname = 'tcp'
	for port in [25, 80]:
		print "Port:%s => service name:%s" % \
		(port, socket.getservbyport(port, protocolname))
		print "Port:%s => service name:%s" % \
		(53, socket.getservbyport(53, 'udp'))

if __name__ == '__main__':
	find_service_name()