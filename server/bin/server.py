# -*- coding:utf-8 -*-
# author: Kai Zhang
# 服务器
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # find the root path
sys.path.append(BASE_DIR)

from core import main

if __name__ == '__main__':
    '''open in right way'''
    main.run()