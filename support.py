# -*- coding: utf-8 -*-
import urllib.error
import urllib.request
import urllib.parse
import json
import zlib
import time
import math
import re
# from biclass import *

# import xml.dom.minidom
# import hashlib
# import sys
# import os

# from getAssDanmaku import *

def getRE(content, regexp):
    return re.findall(regexp, content, re.S)

def getREsearch(content, regexp):
    return re.search(regexp, content, re.S)

def getREsub(content, repl, regexp):
    return re.sub(regexp, repl, content, re.S)

def getURLContent(url, cookie=''):
    """
    功能:
        从url获取内容
    依赖:
        urllib.error
        urllib.request
        zlib
        time
    """
    while True:
        flag = True
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                'Accept-Encoding': 'gzip',
                'Cookie': cookie
            }
            req = urllib.request.Request(url, headers=headers)
            page = urllib.request.urlopen(req)
            content = page.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(e.code, '服务器表示并没有找到网站...')
                return ''
            elif e.code == 403:
                print(e.code, '服务器傲娇地拒绝了访问请求...')
                return ''
            flag = False
            time.sleep(5)
        except urllib.error.URLError as e:
            print(e.reason, '请检测网络连接...')
            return ''
        if flag: 
            break
        print('尝试重新连接...')
    if page.getheader('Content-Encoding') == 'gzip':
        content = str(zlib.decompress(content, 16+zlib.MAX_WBITS), 'utf-8')
    return content

class JsonInfo():
    """
    功能: 
        处理json数据
    依赖:
        json
    """
    def __init__(self, content, pre_deal=lambda x:x):
        self.info = json.loads(pre_deal(content))
        self.error = False
        # print(self.info)
        # 1
        if 'code' in self.info and self.info['code'] != 0:
            
            if 'msg' in self.info:
                # print("[Error] code={0}, msg={1}".format(self.info['code'], self.getValue('msg')))
                self.ERROR_MSG = self.getValue('message')
            elif 'error' in self.info:
                # print("[Error] code={0}, msg={1}".format(self.info['code'],  self.getValue('error')))
                self.ERROR_MSG = self.getValue('error')
            self.error = True
        # 2
        if 'error' in self.info and 'code' in self.info['error']:
            # print("[Error] code={0}, msg={1}".format(self.info['error']['code'], self.info['error']['message']))
            self.ERROR_MSG = self.info['error']['message']
            self.error = True


    def getValue(self, *keys):
        if len(keys) == 0:
            return None
        if keys[0] in self.info:
            temp = self.info[keys[0]]
        else:
            return None
        if len(keys) > 1:
            for key in keys[1:]:
                if type(temp) == dict and key in temp:
                    temp = temp[key]
                else:
                    return None
        return temp

    def __getitem__(self, keys):  # 重载 []
        if not isinstance(keys, tuple):
            keys = (keys,)

        if len(keys) == 0:
            return None

        if keys[0] in self.info:
            temp = self.info[keys[0]]
        else:
            return None

        if len(keys) > 1:
            for key in keys[1:]:
                if type(temp) == dict and key in temp:
                    temp = temp[key]
                else:
                    return None
        return temp


    def keys(self):
        return self.info.keys()



def num2time(num):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(num))

def num2duration(num):
    m = num // 60
    s = num - m*60
    return '{0:0>2}:{1:0>2}'.format(m, s)
    # return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(num))

def UrlEncode(content):
    return urllib.parse.quote(content)




