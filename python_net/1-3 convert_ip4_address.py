#!/usr/bin/env python
#This program is optimized for Python 2.7.

import socket
from binascii import hexlify
#hexadcimal representation of binary data

def convert_ip4_address():
	for ip_addr in ['128.0.0.1','192.168.0.1']:
		packed_ip_addr = socket.inet_aton(ip_addr)
		#A string of IP address convert a 32-bit IP address network sequence
		unpacked_ip_addr = socket.inet_ntoa(packed_ip_addr)
		print "IP address:%s => Packed:%s, Unpacked:%s" \
			%(ip_addr, hexlify(packed_ip_addr), unpacked_ip_addr)

if __name__ == '__main__':
	convert_ip4_address()
