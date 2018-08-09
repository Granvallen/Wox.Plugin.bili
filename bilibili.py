# -*- coding: utf-8 -*-

from support import *
from biclass import *
# from getAssDanmaku import *

# 常量定义 #

# 排序方式 #
# 综合
# TYPE_ZONGHE = 'totalrank'
# 收藏
TYPE_SHOUCANG = 'stow'
# 评论数
TYPE_PINGLUN = 'scores'
# 播放数 
TYPE_BOFANG = 'click' # 也可以使用 'hot'
# 硬币数
TYPE_YINGBI = 'coin'
# 弹幕数
TYPE_DANMU = 'dm'
# 投稿时间 在给定时段内从新到旧排列 
TYPE_TOUGAO = 'pubdate'


# b站分区序号
bilizone = {
    0 : [0, 1, 13, 167, 3, 129, 4, 36, 160, 119, 155, 165, 5, 181, 177, 23, 11],
    1 : [24, 25, 47],
    13 : [33, 32, 51, 152],
    167 : [153, 168, 169, 170],
    3 : [28, 31, 30, 59, 29, 54, 130],
    129 : [20, 154, 156],
    4 : [17, 171, 172, 65, 173, 121, 136, 19],
    36 : [124, 122, 39, 96, 95, 98, 176],
    160 : [138, 21, 76, 75, 161, 162, 163, 174],
    119 : [22, 26, 126, 127],
    155 : [157, 158, 164, 159],
    165 : [166],
    5 : [71, 137, 131],
    181 : [182, 183, 85, 184, 86],
    177 : [37, 178, 179, 180],
    23 : [147, 145, 146, 83],
    11 : [185, 187]
}

# 常量定义结束 #

def getHotVideo(begintime, endtime, tid=33, sortType=TYPE_BOFANG, page=1, pagesize=20, original=False):
    """
    功能:
        获取各区视频排行榜
    输入: 
        begintime: 起始时间, 三元数组[year1, month1, day1] 如 [2018, 8, 2]
        endtime: 终止时间, 三元数组[year2, month2, day2]
        sortType: 字符串, 排序方式, 参照TYPE_开头的常量
        tid: 整数, 投稿分区序号, 参照文档说明
        page: 整数, 页数, 默认1
        pagesize: 单页拉取的视频数, 默认是20, 上限100
    返回: 
        1.视频列表, 列表中的Video类包含AV号, 标题, 观看数, 收藏数, 弹幕数, 投稿日期, 封面, UP的id号和名字, tag, 视频描述, 视频地址, 评论数等, 具体见参考文档
        2.实际爬取的b站排行页面url, 便于查错, 可以使用'_'不接收该返回值
    备注:
        时间间隔应小于3个月
    """
    #判断是否原创
    if original:
        ori1 = '&copy_right=1'
        ori2 = '&original=true'
    else:
        ori1 = '&copy_right=-1'
        ori2 = ''

    url1 = 'https://s.search.bilibili.com/cate/search?main_ver=v3&search_type=video&view_type=hot_rank&pic_size=160x100&cate_id={0}&order={1}&time_from={2[0]}{2[1]:0>2}{2[2]:0>2}&time_to={3[0]}{3[1]:0>2}{3[2]:0>2}&page={4}&pagesize={5}{6}'.format(tid, sortType, begintime, endtime, page, pagesize, ori1)

    # url1 = 'https://api.bilibili.com/archive_rank/getarchiverankbypartion?&type=jsonp&tid={0}&pn={1}{2}'.format(tid, page, ori1)

    url2 = 'https://www.bilibili.com/list/rank-{0}.html#!&order={1}&range={2[0]}-{2[1]:0>2}-{2[2]:0>2}%2C{3[0]}-{3[1]:0>2}-{3[2]:0>2}&page={4}{5}'.format(tid, sortType, begintime, endtime, page, ori2)
    jsoninfo = JsonInfo(getURLContent(url1))
    VideoList = []
    if jsoninfo.error:
        return VideoList, url2
    for video_idx in iter(jsoninfo['result']):
        video = Video(video_idx['id'], video_idx['title'])
        video.play = video_idx['play']
        video.desc = video_idx['description']
        video.pubdate = video_idx['pubdate']
        video.review = video_idx['review']
        video.pic = video_idx['pic']
        video.mid = video_idx['mid']
        video.arcurl = video_idx['arcurl']
        video.tag = video_idx['tag'].split(',')
        video.danmaku = video_idx['video_review']
        video.author = video_idx['author']
        video.favorites = video_idx['favorites']
        video.duration = num2duration(video_idx['duration'])
        video.type = video_idx['type']
        VideoList.append(video)
    return VideoList, url2


def getVideoInfo(aid, pid=1):
    """
    功能:
        由av号获取视频信息
    输入: 
        aid: av号
    返回:
        视频类video
    """
    url1 = 'https://www.bilibili.com/video/av{0}/?p={1}'.format(aid, pid)
    content = getURLContent(url1)
    VideoInfo = getREsearch(content, r'<script>window.__INITIAL_STATE__=({.*});\(')
    if VideoInfo:
        VideoInfo = VideoInfo.group(1)
        # print(VideoInfo)
    else:
        # print('正则表达式寻找视频信息失败(')
        return None
    jsoninfo = JsonInfo(VideoInfo)
    if jsoninfo.error:
        return None

    video = Video(aid)
    video.pid = 1
    video.videos = 1
    if 'aid' in jsoninfo.keys(): # 判断一下是不是番剧
        # 非番剧
        video.tid = jsoninfo['videoData', 'tid']
        video.videos = jsoninfo['videoData', 'videos']
        video.pid = pid if pid <= video.videos else 1
        video.tname = jsoninfo['videoData', 'tname']
        video.pic = jsoninfo['videoData', 'pic']
        video.title = jsoninfo['videoData', 'title']
        video.pubdate = num2time(jsoninfo['videoData', 'pubdate']) # 看下这里pubtime有没有可能为字符串 否则处理错误
        video.ctime = num2time(jsoninfo['videoData', 'ctime'])
        video.desc = jsoninfo['videoData', 'desc']
        video.state = jsoninfo['videoData', 'state']
        video.attribute = jsoninfo['videoData', 'attribute']
        video.duration = num2duration(jsoninfo['videoData', 'pages'][video.pid-1]['duration'])
        video.mid = jsoninfo['videoData', 'owner', 'mid']
        video.face = jsoninfo['videoData', 'owner', 'face']
        video.name = jsoninfo['videoData', 'owner', 'name']
        video.dislike = jsoninfo['videoData', 'stat', 'dislike']
        video.cid = jsoninfo['videoData', 'pages'][video.pid-1]['cid'] # 提示错误 不明 运行没问题
        video.tag = []
        for tag in iter(jsoninfo['tags']):
            video.tag.append(tag['tag_name'])    
    else:
        # 番剧
        video.season_id = jsoninfo['mediaInfo', 'season_id']
        video.season_title = jsoninfo['mediaInfo', 'season_title']
        video.season_status = jsoninfo['mediaInfo', 'season_status']
        video.season_type = jsoninfo['mediaInfo', 'season_type']
        video.allow_bp = jsoninfo['rightsInfo', 'allow_bp']
        video.allow_download = jsoninfo['rightsInfo', 'allow_download']
        video.allow_review = jsoninfo['rightsInfo', 'allow_review']
        video.cover = jsoninfo['epInfo', 'cover']
        video.title = jsoninfo['mediaInfo', 'title']
        video.index_title = jsoninfo['epInfo', 'index_title']
        video.jp_title = jsoninfo['mediaInfo', 'jp_title']
        video.index = jsoninfo['epInfo', 'index']
        video.pubdate = jsoninfo['epInfo', 'pub_real_time'] # 看下这里pubtime有没有可能为字符串
        video.desc = jsoninfo['mediaInfo', 'evaluate']
        video.duration = num2duration(jsoninfo['epInfo', 'duration'] // 1000)
        video.mid = jsoninfo['epInfo', 'mid']
        video.face = jsoninfo['upInfo', 'avatar']
        video.name = jsoninfo['upInfo', 'uname']
        video.cid = jsoninfo['epInfo', 'cid']
        video.style = jsoninfo['mediaInfo', 'style']
        video.media_id = jsoninfo['mediaInfo', 'media_id']
        video.area = jsoninfo['area']
        video.actors = jsoninfo['mediaInfo', 'actors']
        video.episode_status = jsoninfo['epInfo', 'episode_status']
    # 获取视频热度信息 播放量 硬币 收藏 评论 分享 弹幕
    jsoninfo = getVedioStat(video.aid)
    video.play = jsoninfo['view']
    video.danmaku = jsoninfo['danmaku']
    video.review = jsoninfo['reply']
    video.favorite = jsoninfo['favorite']
    video.coin = jsoninfo['coin']
    video.share = jsoninfo['share']
    video.like = jsoninfo['like']
    video.now_rank = jsoninfo['now_rank']
    video.his_rank = jsoninfo['his_rank']
    video.copyright = jsoninfo['copyright']

    # 获取当前观看人数
    video.online_count = getOnlineCount(video.aid, video.cid)

    # 视频地址
    video.arcurl = getREsub(url1, str(video.pid), '(\d+)$')

    return video

def biliVideoSearch(keyword, sortType=TYPE_BOFANG, duration=0, tids_1=0, tids_2=0, page=1):
    """
    功能:
        根据关键词搜索视频
    输入: 
        keyword: 关键词
        order: 排序方式, 参照TYPE_开头的常量
        duration: 视频时长, 0:全部时长 1:10分钟以下 2:10-30分钟 3:30-60分钟 4:60分钟以上
        tids_1: 一级分区序号, 见文档
        tids_2: 二级分区序号
        page: 页码
    返回:
        视频列表
        获取信息地址
    备注:
        该函数不能获取番剧剧集, 搜索番剧请用
    """
    url = 'https://search.bilibili.com/video?keyword={0}&order={1}&duration={2}&tids_1={3}&tids_2={4}&page={5}'.format(UrlEncode(keyword), sortType, duration, tids_1, tids_2, page)
    content = getURLContent(url) # 惊了 事实证明只要请求header有cookie字段就能正常返回信息
    VideoInfo = getREsearch(content, r'<script>window.__INITIAL_STATE__(.?)=(.?)({.*});(.?)\(')
    # print(VideoInfo.group(3))
    if VideoInfo:
        VideoInfo = VideoInfo.group(3) # 获取捕获组
        jsoninfo = JsonInfo(VideoInfo)
        if jsoninfo['apiErrorCode'] != 0: # 确认是否成功获取搜索信息
            # print('获取搜索信息失败(')
            return [], url
    else:
        # print('正则表达式查找视频信息失败(')
        return [], url
    # print(jsoninfo.info)
    VideoList = []
    for video_idx in iter(jsoninfo['videoData']):
        video = Video(video_idx['id'], getREsub(video_idx['title'], '', '<[^>]+>')) # 若title有关键字会被标记
        video.play = video_idx['play']
        video.desc = video_idx['description']
        video.pubdate = num2time(video_idx['pubdate'])
        video.review = video_idx['review']
        video.pic = video_idx['pic']
        video.mid = video_idx['mid']
        video.arcurl = video_idx['arcurl']
        video.tag = video_idx['tag'].split(',')
        video.danmaku = video_idx['video_review']
        video.author = video_idx['author']
        video.favorites = video_idx['favorites']
        video.duration = video_idx['duration']
        video.type = video_idx['type']
        video.arcurl = 'https://www.bilibili.com/video/av{0}'.format(video.aid)
        VideoList.append(video)
    return VideoList, url



def biliBangumiSearch(keyword, page=1):
    url1 = 'https://search.bilibili.com/bangumi?keyword={0}&page={1}'.format(UrlEncode(keyword), page)
    content = getURLContent(url1)
    VideoInfo = getREsearch(content, r'<script>window.__INITIAL_STATE__(.?)=(.?)({.*});(.?)\(')
    # print(VideoInfo.group(3))
    if VideoInfo:
        VideoInfo = VideoInfo.group(3) # 获取捕获组
        jsoninfo = JsonInfo(VideoInfo)
        if jsoninfo['apiErrorCode'] != 0: # 确认是否成功获取搜索信息
            # print('获取搜索信息失败(')
            return [], url1
    else:
        # print('正则表达式查找视频信息失败(')
        return [], url1
    # print(VideoInfo)
    media_id = getRE(VideoInfo, r'"media_id":(\d+),')
    media_score = getRE(VideoInfo, r'"media_score":(.+?),"c')
    bangumis = []
    for idx, val in enumerate(media_id):
        url2 = 'https://bangumi.bilibili.com/view/web_api/season?media_id=' + val
        jsoninfo = JsonInfo(getURLContent(url2))
        result = jsoninfo['result']
        # print(result['alias'])
        bangumi = Bangumi()
        bangumi.cover = result['cover']
        bangumi.actors = result['actors']
        bangumi.alias = result['alias']
        bangumi.areas_id = result['areas'][0]['id']
        bangumi.areas_name = result['areas'][0]['name']
        bangumi.evaluate = result['evaluate']
        bangumi.jp_title = result['jp_title']
        bangumi.link = result['link']
        bangumi.media_id = result['media_id']
        bangumi.newest_ep = result['newest_ep']
        bangumi.is_finish = result['publish']['is_finish']
        bangumi.is_started = result['publish']['is_started']
        bangumi.pub_time = result['publish']['pub_time']
        bangumi.weekday = result['publish']['weekday']
        bangumi.season_status = result['season_status']
        bangumi.season_title = result['season_title']
        bangumi.season_type = result['season_type']
        bangumi.square_cover = result['square_cover']
        bangumi.staff = result['staff']
        bangumi.coins = result['stat']['coins']
        bangumi.danmakus = result['stat']['danmakus']
        bangumi.favorites = result['stat']['favorites']
        bangumi.views = result['stat']['views']
        bangumi.reply = result['stat']['reply']
        bangumi.share = result['stat']['share']
        bangumi.style = result['style']
        bangumi.title = result['title']
        bangumi.total_ep = result['total_ep']
        bangumi.pub_ep = int(result['newest_ep']['index'])
        # 评分
        if media_score[idx] != 'null':
            scoreinfo = JsonInfo(media_score[idx])
            bangumi.score = scoreinfo['score']
            bangumi.user_count = scoreinfo['user_count']
        # 剧集列表
        episodes = []
        for ep in result['episodes']:
            episode = Episode()
            episode.title = bangumi.title
            episode.aid = ep['aid']
            episode.cid = ep['cid']
            episode.cover = ep['cover']
            episode.duration = num2duration(ep['duration'] // 1000)
            episode.ep_id = ep['ep_id'] # 剧集号
            episode.episode_status = ep['episode_status']
            episode.From = ep['from']
            episode.index = ep['index'] # 第几话
            episode.index_title = ep['index_title'] # 该话标题
            episode.pub_real_time = ep['pub_real_time'] # 发布时间
            if episode.ep_id:
                episode.link = 'https://www.bilibili.com/bangumi/play/ep{0}'.format(episode.ep_id) # 观看地址
            # 热度信息   这里要获取热度信息 与 在线人数 很费时间
            # url3 = 'https://api.bilibili.com/x/web-interface/archive/stat?aid={0}'.format(episode.aid)
            # stat = JsonInfo(getURLContent(url3))
            # episode.play = stat['data', 'view']
            # episode.danmaku = stat['data', 'danmaku']
            # episode.review = stat['data', 'reply']
            # episode.favorite = stat['data', 'favorite']
            # episode.coin = stat['data', 'coin']
            # episode.share = stat['data', 'share']
            # episode.like = stat['data', 'like']
            # episode.now_rank = stat['data', 'now_rank']
            # episode.his_rank = stat['data', 'his_rank']
            # 在线人数
            # url4 = 'https://interface.bilibili.com/player?id=cid:{0}&aid={1}'.format(episode.cid, episode.aid)
            # online_count = getREsearch(getURLContent(url4), r'<online_count>(\d+)</online_count>')
            # if online_count:
            #     episode.online_count = online_count.group(1)
            # else:
            #     print('获取在线观看人数失败(')
            # up
            episode.mid = ep['mid'] 
            # 不明
            episode.vid = ep['vid']
            episodes.append(episode)

        bangumi.episodes = episodes

        # up
        if 'up_info' in result.keys():
            bangumi.avatar = result['up_info']['avatar']
            bangumi.mid = result['up_info']['mid']
            bangumi.uname = result['up_info']['uname']
        # 权限信息
        bangumi.allow_bp = result['rights']['allow_bp']
        bangumi.allow_download = result['rights']['allow_download']
        bangumi.allow_review = result['rights']['allow_review']
        bangumi.copyright = result['rights']['copyright']
        bangumi.is_preview = result['rights']['is_preview']
        bangumi.watch_platform = result['rights']['watch_platform']
        # 不明
        bangumi.is_paster_ads = result['is_paster_ads']
        bangumi.mode = result['mode']

        bangumis.append(bangumi)
    return bangumis




def getVedioStat(aid):
    """
    获取视频的热度信息, 番剧通用
    """
    url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid={0}'.format(aid)
    stat = JsonInfo(getURLContent(url))
    result = {
        'view' : None,
        'danmaku' : None,
        'reply' : None,
        'favorite' : None,
        'coin' : None,
        'share' : None,
        'like' : None,
        'now_rank' : None,
        'his_rank' : None,
        'copyright' : None
    }
    result['play'] = stat['data', 'view']
    result['danmaku'] = stat['data', 'danmaku']
    result['review'] = stat['data', 'reply']
    result['favorite'] = stat['data', 'favorite']
    result['coin'] = stat['data', 'coin']
    result['share'] = stat['data', 'share']
    result['like'] = stat['data', 'like']
    result['now_rank'] = stat['data', 'now_rank']
    result['his_rank'] = stat['data', 'his_rank']
    result['copyright'] = stat['data', 'copyright']
    return result

def getOnlineCount(aid, cid):
    """
    获取某视频当前在线观看人数, 番剧通用
    """
    url = 'https://interface.bilibili.com/player?id=cid:{0}&aid={1}'.format(cid, aid)
    online_count = getREsearch(getURLContent(url), r'<online_count>(\d+)</online_count>')
    if online_count:
        return online_count.group(1)
    else:
        # print('获取在线观看人数失败(')
        return None





if __name__ == "__main__":
     pass



