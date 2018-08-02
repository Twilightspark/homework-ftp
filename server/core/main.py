# -*- coding:utf-8 -*-
# author: Kai Zhang
import socketserver

from core.server_ftp import FTPServer
from conf.setting import IP_INFO

def run():
    print('服务器已运行！')
    server = socketserver.ThreadingTCPServer((IP_INFO['ip'], IP_INFO['port']), FTPServer)
    server.serve_forever()