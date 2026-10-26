# -*- coding: utf-8 -*-
import re
import requests
from base.spider import Spider  # 继承 Fongmi 官方底层的蜘蛛基类

class Spider(Spider):
    def getName(self):
        # 爬虫在系统里的内部代号
        return 'SoccerFullSpider'

    def init(self, extend=""):
        # 基础主域名与通用请求头配置
        self.host = 'https://soccerfull.net'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.timeout = 10

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def __init__(self):
        # 构造函数
        self.name = '体育全场集锦源'

    # 1. 第一步：下发分类标签（完美注入主页斜杠 '/' 作为最新内容代号）
    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        result['class'].append({'type_name': '最新', 'type_id': '/'})
        result['class'].append({'type_name': '欧冠', 'type_id': '/cate/premier-league'})
        result['class'].append({'type_name': '英超', 'type_id': '/cate/premier-league'})
        result['class'].append({'type_name': '西甲', 'type_id': '/cate/laliga'})
        result['class'].append({'type_name': '德甲', 'type_id': '/cate/bundesliga'})
        result['class'].append({'type_name': '意甲', 'type_id': '/cate/serie-a'})
        result['class'].append({'type_name': '法甲', 'type_id': '/cate/laliga'})
        return result

    def homeVideoContent(self):
        return {}

    # 2. 第二步：根据点击的标签网址和当前页码（pg），去抓取对应的视频封面墙
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        
        # 自动拼接出带页码的分类网页网址
        connect_char = '&' if '?' in tid else '?'
        target_url = f"{self.host}{tid}{connect_char}page={pg}"
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 升级版终极容错正则：完美无视任意数量的空格、换行以及 h2/h3 标签差异
                reg_rule = r'href="([^"]+-[0-9]+\.html)"[\s\S]*?src="([^"]+)"[\s\S]*?<h[23]>([^<]+)</h[23]>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for ep_path, pic_url, name in matches:
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    # 将清洗好的数据，打包塞入符合 Fongmi 规范的卡片列表里
                    vod_list.append({
                        'vod_id': ep_path,            # 让 vod_id 携带完整的网页路径（传给详情页）
                        'vod_name': name.strip(),     # 电视封面上显示的视频标题
                        'vod_pic': pic_url,          # 封面图片直链
                        'vod_remarks': '1080P高清'     # 卡片右下角的备注信息
                    })
                
                result['list'] = vod_list
                result['total'] = len(vod_list)
        except:
            pass
            
        return result

    # 3. 第三步：点击海报进入详情页，通过绝对路径，完美截断洗出无换行错乱的集数按钮
    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        
        vid = ids[0]  # 拿到上一级传过来的完整网页路径（例如 /sunderland-vs-leeds-united-4659.html）
        target_url = self.host + vid  # 100% 拼接出绝对正确的网页真实网址
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 正则第一步：精准斩断获取 <article class="infobv"> 的局部文本块
                article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
                
                play_urls = []
                if article_block:
                    block_text = article_block.group(1)
                    
                    # 正则第二步：循环抠出所有分集的 sid 数字和显示的按钮文本（如 Full Match in En）
                    matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([\s\S]*?)</', block_text)
                    
                    for sid, ep_name in matches:
                        # 强效清洗：彻底剔除掉阻碍电视组件渲染的 \r, \n 换行符以及两端的多余空格
                        clean_name = ep_name.replace('\r', '').replace('\n', '').strip()
                        # 打包成 Fongmi 标准格式：集数名称$选集独立sid (例如：Full Match in En$17964)
                        play_urls.append(f"{clean_name}${sid}")
                
                if not play_urls:
                    # 保底处理
                    play_urls.append(f"正片播放$direct_play")
                
                return {'list': [{
                    'vod_id': vid,
                    'vod_name': '赛事全场高清集锦',
                    'vod_pic': f"{self.host}/imgs/{vid.split('-')[-1].replace('.html', '')}.png", # 根据规律还原图
                    'vod_play_from': '官方高清源',
                    'vod_play_url': '#'.join(play_urls)  # 用 # 号完美隔开集数按钮
                }]}
        except:
            pass
            
        return {'list': []}

    # 4. 第四步：大结局播放解析！当用户在电视点击某个分集按钮时，瞬间完成直链派发
    def playerContent(self, flag, id, vipFlags):
        # 此时传进来的 id 就是我们在第三步打包给按钮的独立 sid 数字（例如 17964）
        
        # 💡 终极终点逻辑：顺藤摸瓜，直接替换并拼接出原网站存放于本地的公共 M3U8 直链地址！
        real_m3u8_url = f"{self.host}/hls/{id}.m3u8"
        
        # 构造电视原生播放器（ExoPlayer/IJKPlayer）拉取切片流时必须携带的伪装 Headers，防止 403 拦截
        player_headers = {
            'User-Agent': self.header['User-Agent'],
            'Referer': 'https://tiktok.com'  # 字节防盗链跳动核心认准的宿主来源
        }
        
        # 宣告通关：将直链和伪装 Headers 直接吐给 Fongmi
        return {
            'parse': 0,  # 0 代表直接让电视进行原生内核硬解，速度最快、画质最高
            'url': real_m3u8_url,
            'header': player_headers
        }

    def searchContent(self, key, quick, pg="1"):
        return {'list': []}

    def fetch(self, url):
        return None

    def localProxy(self, param):
        return None
