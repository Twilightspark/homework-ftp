# -*- coding:utf-8 -*-
# author: Kai Zhang
# class FTPClient
import hashlib
import socket
import json
import os
import sys

from conf.setting import BASE_DIR

class FTPClient(object):
    '''client ftp'''
    def __init__(self):
        self.account = None
        self.password = None
        self.client = socket.socket()
        self.flag = False
        self.path = ''

    def connect(self, ip, port):
        self.client.connect((ip, port))

    def help(self):
        message = '''
        命令帮助
        dir         : 查看当前目录下的文件
        mkdir dir   : 创建目录
        cd folder   : 移动到某一目录下
        put filename: 上传某文件到当前目录
        get filename: 下载某文件从当前目录
        cut filename: 删除某文件从当前目录
        q           : 退出账号
        '''
        print(message)

    def access(self):
        user_account = input('请输入你的账号>>').strip()
        user_password = input('请输入你的密码>>').strip()
        password = hashlib.sha512()
        password.update(user_password.encode('utf-8'))
        info = {
            'func': 'access',
            'account': user_account,
            'password': password.hexdigest()
        }
        self.client.send(json.dumps(info).encode('utf-8'))
        recv_num = int(self.client.recv(1024).decode())
        if recv_num == 100:
            print('登陆成功!')
            self.account = user_account
            self.password = password.hexdigest()
            self.flag = False
            return False
        elif recv_num == 101:
            print('用户密码错误！')
            return True
        elif recv_num == 102:
            print('用户名不存在！')
            return True
        else:
            print('未知错误！')
            return True

    def dir(self, cmd):
        info = {
            'func': 'dir',
            'account': self.account,
            'path': self.path
        }
        self.client.send(json.dumps(info).encode('utf-8'))
        recv_dir = self.client.recv(1024).decode()
        recv_dir = json.loads(recv_dir)
        if recv_dir['size'] == 0:
            print('当前目录为空！')
        else:
            self.client.send(b'ok')
            recv_size = 0
            recv_data = b''
            while recv_size < recv_dir['size']:
                if recv_dir['size'] - recv_size > 1024:
                    size = 1024
                else:
                    size = recv_dir['size'] - recv_size
                data = self.client.recv(size)
                recv_size += len(data)
                recv_data += data
            self.catalog = recv_data.decode()
            print(self.catalog)

    def mkdir(self, new_dir):
        info = {
            'func': 'mkdir',
            'account': self.account,
            'path': self.path,
            'mkdir_path': new_dir
        }
        self.client.send(json.dumps(info).encode('utf-8'))
        recv_dir = self.client.recv(1024).decode()
        recv_dir = json.loads(recv_dir)
        if recv_dir['num'] == 600:
            print(new_dir[1], '目录创建成功')
        elif recv_dir['num'] == 601:
            print('创建的目录已存在')
        else:
            print('未知错误')

    def cd(self, cmd_dir):
        info = {
            'func': 'cd',
            'account': self.account,
            'path': self.path,
            'cd_path': cmd_dir
        }
        self.client.send(json.dumps(info).encode('utf-8'))
        recv_dir = self.client.recv(1024).decode()
        recv_dir = json.loads(recv_dir)
        if recv_dir['num'] == 200:
            if cmd_dir == '.':
                if self.path == '':
                    print('已经到达根目录，无法再向前')
                else:
                    new_path = self.path.split('//')
                    del new_path[-2]
                    self.path = '//'.join(new_path)
            else:
                self.path = self.path + cmd_dir + '//'
        elif recv_dir['num'] == 201:
            print('移动的目录不存在')
        else:
            print('未知错误')

    def put(self, cmd_dir):
        path = BASE_DIR + r'//database//' + self.account + r'//'
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, cmd_dir)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            info = {
                'func': 'put',
                'account': self.account,
                'path': self.path,
                'size': size,
                'name': cmd_dir
            }
            self.client.send(json.dumps(info).encode('utf-8'))
            recv_dir = self.client.recv(1024).decode()
            recv_dir = json.loads(recv_dir)
            if recv_dir['num'] == 300:
                send_flag = True
            elif recv_dir['num'] == 301:
                select = input('文件已存在是否覆盖[Y/N]>>')
                if select == 'y' or select == 'Y':
                    info['recover'] = True
                else:
                    info['recover'] = False
                self.client.send(json.dumps(info).encode('utf-8'))
                self.client.recv(1024)
                send_flag = True
            elif recv_dir['num'] == 302:
                print('存储空间不足，请联系管理员扩充！')
                send_flag = False
            else:
                print('未知错误！')
                send_flag = False
            if send_flag:
                f = open(path, 'rb')
                file_md5 = hashlib.md5()
                send_size = 0
                for i in f:
                    self.client.send(i)
                    file_md5.update(i)
                    send_size += len(i)
                    num = int(send_size/size*20)
                    str1 = "\r[%s%s]已发送%d%%" % ("%" * num, " " * (20 - num), num*5)
                    sys.stdout.write(str1)
                    sys.stdout.flush()
                f.close()
                self.client.send(file_md5.hexdigest().encode('utf-8'))
                print(self.client.recv(1024).decode())
        else:
            print('文件不存在')

    def get(self, cmd_dir):
        info = {
            'func': 'get',
            'account': self.account,
            'path': self.path,
            'name': cmd_dir
        }
        self.client.send(json.dumps(info).encode('utf-8'))
        recv_dir = self.client.recv(1024).decode()
        recv_dir = json.loads(recv_dir)
        if recv_dir['num'] == 400:
            self.client.send('开始接收'.encode('utf-8'))
            path = BASE_DIR + r'//database//' + self.account + r'//'
            if not os.path.exists(path):
                os.makedirs(path)
            f = open(os.path.join(path, cmd_dir), 'wb')
            recv_size = 0
            file_md5 = hashlib.md5()
            while recv_size < recv_dir['size']:
                if recv_dir['size'] - recv_size > 1024:
                    size = 1024
                else:
                    size = recv_dir['size'] - recv_size
                data = self.client.recv(size)
                recv_size += len(data)
                file_md5.update(data)
                f.write(data)
                num = int(recv_size / recv_dir['size'] * 20)
                str1 = "\r[%s%s]已接收%d%%" % ("%" * num, " " * (20 - num), num*5)
                sys.stdout.write(str1)
                sys.stdout.flush()
            f.close()
            md5 = self.client.recv(1024).decode()
            if file_md5.hexdigest() == md5:
                print('接收完毕!')
            else:
                print('文件损坏！')
                os.remove(path)
        elif recv_dir['num'] == 401:
            print('文件不存在！')
        else:
            print('未知错误！')

    def cut(self, cmd_dir):
        info = {
            'func': 'cut',
            'account': self.account,
            'path': self.path,
            'name': cmd_dir
        }
        self.client.send(json.dumps(info).encode('utf-8'))
        recv_dir = self.client.recv(1024).decode()
        recv_dir = json.loads(recv_dir)
        if recv_dir['num'] == 500:
            print('删除完成！')
        elif recv_dir['num'] == 501:
            print('文件不存在！')
        else:
            print('未知错误！')

    def close(self):
        print('客户端关闭')
        self.client.close()

    def __del__(self):
        self.client.close()