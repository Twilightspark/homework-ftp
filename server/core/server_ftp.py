# -*- coding:utf-8 -*-
# author: Kai Zhang
# class FTPServer
import socketserver
import json
import os
import hashlib

from conf.setting import BASE_DIR


class FTPServer(socketserver.BaseRequestHandler):
    '''server ftp'''

    def handle(self):
        while True:
            try:
                self.data = self.request.recv(1024)
                print('客户端地址: %s' % (self.client_address[0]))
                if not self.data:
                    print('客户端断开了')
                    break
                else:
                    self.data = json.loads(self.data.decode())
                    func = self.data['func']
                    if hasattr(self, func):
                        getattr(self, func)()
                    else:
                        print('功能不存在')
            except ConnectionResetError as e:
                print('客户端断开了')
                break

    def access(self):
        account = self.data['account']
        password = self.data['password']
        path = BASE_DIR + r'//database//user//' + account + '.json'
        if os.path.isfile(path):
            f = open(path, 'r')
            data = json.loads(f.read())
            f.close()
            if password == data['password']:
                self.request.send(b'100')
                self.disk_path = data['disk_path']
                self.max_size = float(data['disk_size'])
                print('用户%s登陆成功：%s' % (account, self.client_address[0]))
            else:
                self.request.send(b'101')
        else:
            self.request.send(b'102')

    def dir(self):
        path = self.disk_path + self.data['path']
        data = ''
        print('读取目录：', path)
        for i in os.listdir(path):
            data += i + '\n'
        data = data.encode('utf-8')
        info = {
            'size': len(data)
        }
        self.request.send(json.dumps(info).encode('utf-8'))
        if info['size'] == 0:
            print('目录为空')
        else:
            self.request.recv(1024)
            self.request.send(data)

    def cd(self):
        info = {
            'num': 201
        }
        if self.data['cd_path'] == '.':
            info['num'] = 200
            print('移动到上一级目录')
        else:
            new_path = self.disk_path + self.data['path'] + self.data['cd_path'] + r'//'
            if os.path.isdir(new_path):
                info['num'] = 200
                print('移动到新目录：', new_path)
        self.request.send(json.dumps(info).encode('utf-8'))

    def put(self):
        info = {
            'num': 303
        }
        size = 0
        root_path = self.disk_path
        for root, dirs, files in os.walk(root_path):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        size = size + self.data['size']
        recv_flag = False
        path = root_path
        if size / 1024 / 1024 > self.max_size:
            info['num'] = 302
            self.request.send(json.dumps(info).encode('utf-8'))
        else:
            path = root_path + self.data['path'] + self.data['name']
            if os.path.isfile(path):
                info['num'] = 301
                self.request.send(json.dumps(info).encode('utf-8'))
                data = json.loads(self.request.recv(1024).decode())
                if not data['recover']:
                    path = root_path + self.data['path'] + self.data['name'] + '.new'
                recv_flag = True
                self.request.send('准备完成！'.encode('utf-8'))
            else:
                info['num'] = 300
                self.request.send(json.dumps(info).encode('utf-8'))
                recv_flag = True
        if recv_flag:
            print('客户端上传该路径文件', path)
            f = open(path, 'wb')
            recv_size = 0
            file_md5 = hashlib.md5()
            while recv_size < self.data['size']:
                if self.data['size'] - recv_size > 1024:
                    size = 1024
                else:
                    size = self.data['size'] - recv_size
                data = self.request.recv(size)
                recv_size += len(data)
                file_md5.update(data)
                f.write(data)
            f.close()
            md5 = self.request.recv(1024).decode()
            if file_md5.hexdigest() == md5:
                print('接收完毕:', path)
                self.request.send('接收完毕！'.encode('utf-8'))
            else:
                print('文件损坏！')
                self.request.send('文件损坏！'.encode('utf-8'))
                os.remove(path)

    def get(self):
        info = {
            'num': 402
        }
        path = self.disk_path + self.data['path'] + self.data['name']
        print('客户端请求该路径文件', path)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            info['num'] = 400
            info['size'] = size
            send_flag = True
        else:
            info['num'] = 401
            send_flag = False
        self.request.send(json.dumps(info).encode('utf-8'))
        if send_flag:
            self.request.recv(1024)
            f = open(path, 'rb')
            file_md5 = hashlib.md5()
            for i in f:
                self.request.send(i)
                file_md5.update(i)
            f.close()
            self.request.send(file_md5.hexdigest().encode('utf-8'))

    def cut(self):
        info = {
            'num': 502
        }
        path = self.disk_path + self.data['path'] + self.data['name']
        print('客户端删除该路径文件', path)
        if os.path.isfile(path):
            os.remove(path)
            info['num'] = 500
        else:
            info['num'] = 501
        self.request.send(json.dumps(info).encode('utf-8'))

    def mkdir(self):
        info = {
            'num': 602
        }
        new_path = self.disk_path + self.data['path'] + self.data['mkdir_path']
        print('客户端请求新建该路径', new_path)
        if os.path.exists(new_path):
            info['num'] = 601
            print('要创建的目录已存在')
        else:
            info['num'] = 600
            os.makedirs(new_path)
            print('创建新目录', new_path)
        self.request.send(json.dumps(info).encode('utf-8'))
