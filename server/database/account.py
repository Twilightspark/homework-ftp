# -*- coding:utf-8 -*-
# author: Kai Zhang
# admin account
import os
import sys
import json
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # find the root path
sys.path.append(BASE_DIR)

user_dic = {}
user_dic['account'] = input('请输入你的账号>>').strip()
un_password = input('请输入你的密码>>').strip()
disk_size = input('请输入你的磁盘可用大小(MB)>>').strip()
user_dic['disk_size'] = disk_size
password = hashlib.sha512()
password.update(un_password.encode('utf-8'))
user_dic['password'] = password.hexdigest()
print('用户信息为：%s'%(user_dic))
path = BASE_DIR + r'\\user\\' +  user_dic['account'] + '.json'
f = open(path, 'w')
f.write(json.dumps(user_dic))
f.close()

