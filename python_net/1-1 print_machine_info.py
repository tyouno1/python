#!/usr/bin/env python
#This program is optimized for Python 2.7.

import socket

def print_machine_info():
	host_name = socket.gethostname()
	ip_address = socket.gethostbyname(host_name)
	print "Host name:%s" % host_name
	print "IP address:%s" % ip_address

	ip_address = '127.0.0.1'
	result = socket.gethostbyaddr(ip_address)
	print "Host name:%s" % result[0]
	print "IP address:%s" % ip_address

if __name__ == '__main__':
	print_machine_info()