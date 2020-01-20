# -*- coding:utf-8 -*-
# author: Kai Zhang

from core.client_ftp import FTPClient
# from core.account import Account
from conf.setting import IP_INFO

def interactive(client):
    client.help()
    inter_flag = True
    while inter_flag:
        cmd_data = input('请输入命令>>').strip()
        if cmd_data == 'q':
            client.close()
            inter_flag = False
        else:
            try:
                """放入测试语句"""
                check_index = cmd_data.index(' ')
                cmd_dir = cmd_data[check_index + 1:]
                func = cmd_data[:check_index]
            except Exception as e:
                """放入异常处理"""
                func = cmd_data
                cmd_dir = ''
            if hasattr(client, func):
                action = getattr(client, func)
                action(cmd_dir)
            else:
                client.help()
                print('输入命令不存在')

def run():
    print('客户端已运行！')
    client = FTPClient()
    client.connect(IP_INFO['ip'], IP_INFO['port'])
    access_flag = True
    access_num = 5
    while access_flag and access_num > 0:
        access_flag = client.access()
        if access_flag:
            access_num = access_num - 1
            print('你还有%d次机会'%(access_num))

    if not access_flag:
        interactive(client)