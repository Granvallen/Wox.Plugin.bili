# -*- coding: utf-8 -*-

# 8dc60356-d87d-436c-9399-2ebae0a66c35

from wox import Wox, WoxAPI
from bilibili import *
import os
# import subprocess
# import win32con
# import win32api

# 排序方式
sortby = {
    'sc' : TYPE_SHOUCANG,
    'pl' : TYPE_PINGLUN,
    'bf' : TYPE_BOFANG,
    'yb' : TYPE_YINGBI,
    'dm' : TYPE_DANMU,
    'tg' : TYPE_TOUGAO
}

bangumi_stat = [['未开播', '未开播'], ['连载中', '已完结']]



class bili(Wox):

    def query(self, query):

        # 参数初始化
        VideoList = []
        BangumiList = []
        videos = []
        bangumis = []
        mode = ''
        keyword = ''
        sortType = TYPE_BOFANG
        duration = 0
        tids_1 = 0
        tids_2 = 0
        page = 1
        aid = 0
        pid = 1
        begintime = []
        endtime = []
        day = 3

        if not query or query == '-':   # 没有参数
            return bili.helpmsg(self, '-s 搜索视频 / -b 搜索番剧 / -a 用av号查找视频 / -h 热门视频排行榜', '少女祈祷中...', 'help')

        keys = query.split()

        # 解析模式
        mode = ''
        mode = getREsearch(keys[0], r'^-([sahb])$')
        if mode:
            mode = mode.group(1)
        else:
            return bili.helpmsg(self, '-s 搜索视频 / -b 搜索番剧 / -a 用av号查找视频 / -h 热门视频排行榜', '模式匹配错误, 请检查格式...', 'error')

        if mode == 's':  # s mode
            if len(keys) > 1:
                # 参数更新
                keyword = keys[1].replace(',', ' ')
                if len(keys) > 2:
                    keys = ''.join(keys[2:])
                    # sortType
                    for idx in sortby.keys(): 
                        if idx in keys:
                            sortType = sortby[idx]
                            keys = keys.replace(idx, '')
                            break
                    # duration
                    d = getREsearch(keys, r'd(\d+)')
                    if d:
                        duration = int(d.group(1))
                        keys = keys.replace('d'+d.group(1), '')
                    # tid
                    t = getREsearch(keys, r't(\d+)')
                    if t:
                        t = t.group(1)
                        keys = keys.replace('t'+t, '')
                        if int(t) in bilizone[0]: 
                            tids_1 = int(t) # t为一级分区
                        else:
                            for key, val in bilizone.items(): # 找一下t的一级分区
                                if int(t) in val:
                                    tids_1 = key
                                    tids_2 = int(t)
                                    break
                    # page
                    p = getREsearch(keys, r'p(\d+)')
                    if p:
                        page = int(p.group(1))
                        keys = keys.replace('p'+p.group(1), '')
                VideoList, _ = biliVideoSearch(keyword, sortType, duration, tids_1, tids_2, page)

                # bug : 整理好顺序的数组返回给wox, wox显示顺序依旧会不同 此处验证传过去顺序是对的 问题可能与wox显示项目机制有关 其他插件也有这个问题 另外用tab键切换选项会跳
                # helpmsg[0]['Title'] = keyword + sortType + str([duration, tids_1, tids_2, page])
                # return helpmsg
                i = 1 # 用于指明排序
                for video_idx in VideoList:
                    video = {
                        'Title': '{0} {1} [{2}]  av {3}'.format(i, video_idx.title, video_idx.pubdate[:-3], video_idx.aid),
                        'SubTitle': 'UP {0}   {1}'.format(video_idx.author, re.sub('[\r\n]', '', video_idx.desc)),
                        'IcoPath': 'img/icon.png',
                        'JsonRPCAction' : {
                            'method' : 'playVideo',
                            'parameters' : [video_idx.arcurl],
                            'dontHideAfterAction' : False
                        }
                    }
                    videos.append(video)
                    i += 1
                # helpmsg[0]['Title'] = videos[0]['Title']
                # os.system(videos[0]['Title'])
                # return helpmsg
                return videos
            else:
                return bili.helpmsg(self, '搜索视频 bili -s 关键字 [缩小范围选项]', '多个关键字用逗号分隔', 'help')
        elif mode == 'a': # a mode
            if len(keys) > 1:
                # 更新参数
                try:
                    aid = int(keys[1])
                except:
                    return bili.helpmsg(self, 'av号找视频 bili -a av号 [分p号]', 'av号应该是数字...', 'error')
                if len(keys) > 2:
                    keys = ''.join(keys[2:])
                    # pid 分p号
                    p = getREsearch(keys, r'p(\d+)')
                    if p:
                        pid = int(p.group(1))
                        keys = keys.replace('p'+p.group(1), '')

                video_idx = getVideoInfo(aid, pid)   # bug : 这里有问题 原本若没有这个av号函数返回None 但这里若没有会卡在函数里 这个函数在其他地方调试通过 此处bug原因不明 调试发现卡在 jsoninfo = JsonInfo(VideoInfo)
                # bug 解决了 是JsonInfo类中的print函数影响 但原因依旧不明
                if not video_idx:
                    return bili.helpmsg(self, '未找到该av号的视频...', '', 'empty')
                
                video = {
                    'Title': '{0} [{1}p][{2}] 在线人数 {3} cid {4}'.format(video_idx.title, video_idx.videos, video_idx.pubdate[:-3], video_idx.online_count, video_idx.cid),
                    'SubTitle': 'UP {0}   {1}'.format(video_idx.name, re.sub('[\r\n]', '', video_idx.desc)),
                    'IcoPath': 'img/icon.png',
                    'JsonRPCAction' : {
                        'method' : 'playVideo',
                        'parameters' : [video_idx.arcurl],
                        'dontHideAfterAction' : False
                    }
                }
                videos.append(video)
                # helpmsg[0]['Title'] = videos[0]['Title']
                # return helpmsg
                return videos
            else:
                return bili.helpmsg(self, 'av号找视频 bili -a av号 [分p号]', '基本不会用的功能...', 'help')
        elif mode == 'h': # h mode
            if len(keys) > 1:
                keys = ''.join(keys[1:])
                # tids_2
                t = getREsearch(keys, r't(\d+)')
                if t:
                    temp = int(t.group(1))
                    keys = keys.replace('t'+t.group(1), '')
                else:
                    return bili.helpmsg(self, '热门视频 bili -h 分区序号 [其他选项]', '分区序号是必须的', 'help')
                for idx in bilizone[0][1:]:
                    if temp in bilizone[idx]:
                        tids_2 = temp
                        break
                if tids_2 == 0:
                    return bili.helpmsg(self, '热门视频 bili -h 分区序号 [其他选项]', '该子分区不存在...', 'error')
                # sortType
                for idx in sortby.keys():
                    if idx in keys:
                        sortType = sortby[idx]
                        keys = keys.replace(idx, '')
                        break
                # page
                p = getREsearch(keys, r'p(\d+)')
                if p:
                    page = int(p.group(1))
                    keys = keys.replace('p'+p.group(1), '')
                # begintime endtime
                d = getREsearch(keys, r'd(\d+)')
                if d:
                    day = int(d.group(1))
                    keys = keys.replace('d'+d.group(1), '')
                if day > 90:
                    day = 3
                endtime = time.strftime('%Y %m %d', time.localtime(time.time())).split()
                begintime = time.strftime('%Y %m %d', time.localtime(time.time() - day*86400)).split()

                VideoList, _ = getHotVideo(begintime, endtime, tids_2, sortType, page, pagesize=20, original=False)
                i = 1 # 用于指明排序
                for video_idx in VideoList:
                    video = {
                        'Title': '{0} {1} [{2}] av {3}'.format(i, video_idx.title, video_idx.pubdate[:-3], video_idx.aid),
                        'SubTitle': 'UP {0}   {1}'.format(video_idx.author, re.sub('[\r\n]', '', video_idx.desc)),
                        'IcoPath': 'img/icon.png',
                        'JsonRPCAction' : {
                            'method' : 'playVideo',
                            'parameters' : [video_idx.arcurl],
                            'dontHideAfterAction' : False
                        }
                    }
                    videos.append(video)
                    i += 1
                return videos
            else:
                return bili.helpmsg(self, '热门视频 bili -h 分区序号 [其他选项]', '分区序号是必须的', 'help')
        elif mode == 'b': # b mode
            if len(keys) > 1:
                keyword = keys[1].replace(',', ' ')

                if len(keys) > 2:
                    keys = ''.join(keys[2:])
                    # pid 这里作为选择的集数
                    p = getREsearch(keys, r'p(\d+)')
                    if p:
                        pid = int(p.group(1))
                        keys = keys.replace('p'+p.group(1), '')

                BangumiList = biliBangumiSearch(keyword, page=1)

                bangumis = [] # 返回的番剧列表
                for bangumi_idx in BangumiList:
                    p = pid
                    if bangumi_idx.pub_ep >= pid >= 1:
                        # return bili.helpmsg(self, str(bangumi_idx.pub_ep), '多个关键字用逗号分隔', 'help')
                        link = (bangumi_idx.episodes)[pid-1].link
                    else:
                        # return bili.helpmsg(self, str(pid), '多个关键字用逗号分隔', 'help')
                        p = 1
                        link = (bangumi_idx.episodes)[0].link
                    bangumi = {
                        'Title': '{0} [{1}] [{2}/{3}话] -> 第{4}话'.format(bangumi_idx.title, bangumi_stat[bangumi_idx.is_started][bangumi_idx.is_finish], bangumi_idx.pub_ep, bangumi_idx.total_ep, p),
                        'SubTitle': 'UP {0}   {1}'.format(bangumi_idx.uname, re.sub('[\r\n]', '', bangumi_idx.evaluate)),
                        'IcoPath': 'img/icon.png',
                        'JsonRPCAction' : {
                            'method' : 'playVideo',
                            'parameters' : [link],
                            'dontHideAfterAction' : False
                        }
                    }
                    bangumis.append(bangumi)
                return bangumis

            else:
                return bili.helpmsg(self, '搜索番剧 bili -b 关键字 [话数]', '多个关键字用逗号分隔', 'help')
        else:
            return bili.helpmsg(self, '-s 搜索视频 / -b 搜索番剧 / -a 用av号查找视频 / -h 热门视频排行榜', '模式匹配错误, 请检查格式...', 'error')


    def helpmsg(self, title, subtitle, icon):
        msg = [{
            'Title': title,
            'SubTitle': subtitle,
            'IcoPath': 'img/{0}.png'.format(icon)
        }]
        return msg
        

    def playVideo(self, arcurl):
        os.popen('cmd /c playVideo.vbs ' + arcurl)
        # subprocess.Popen('cmd /c playVideo.vbs ' + arcurl)
        
        # python 执行dos命令实现
        # time.sleep(3)
        # win32api.keybd_event(70, 0, 0, 0)
        # win32api.keybd_event(70, 0, win32con.KEYEVENTF_KEYUP, 0)
        # time.sleep(0.5)
        # win32api.keybd_event(32, 0, 0, 0)
        # win32api.keybd_event(32, 0, win32con.KEYEVENTF_KEYUP, 0)




# 必须有以下语句
if __name__ == '__main__':
    bili()