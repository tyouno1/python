#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import socket
import threading
import SocketServer

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Client received:%s" % response
    finally:
        sock.close()

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        current_thread = threading.current_thread()
        response = '%s:%s' % (current_thread.name, data)
        self.request.sendall(response)

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':
    server = ThreadingTCPServer(('localhost', 0), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target = server.serve_forever)
    #使用threading.thread(target="")指明函数入口,调用serve_forever方法启动服务器并使其对这个连接可用。
    #BaseServer.serve_forever(poll_interval=0.5): 处理请求，直到一个明确的shutdown()请求。
    #每poll_interval秒轮询一次shutdown。忽略self.timeout。如果你需要做周期性的任务，建议放置在其他线程。
    server_thread.setDaemon(False)#setDaemon主线程结束时，会把子线程也杀死
    server_thread.start()
    print "Server loop running on thread:%s" % server_thread.name

    client(ip, port, "mess is 1")
    client(ip, port, "mess is 2")
    client(ip, port, "mess is 3")

    server.shutdown()



