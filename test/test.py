# -*- coding: utf-8 -*-
import re
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        # 内部系统代号，保持干净的英文
        return 'SoccerFullSpider'

    def init(self, extend=""):
        # 基础主域名配置
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
        self.name = '体育全场集锦源'

    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        result['class'].append({'type_name': '最新赛事', 'type_id': '/'})
        result['class'].append({'type_name': '英超联赛', 'type_id': '/premier-league.html'})
        result['class'].append({'type_name': '西甲联赛', 'type_id': '/laliga.html'})
        result['class'].append({'type_name': '欧冠剧场', 'type_id': '/champions-league.html'})
        return result

    def homeVideoContent(self):
        return {}

    # 第二步修复：采用最高效、绝不报错的字符串拆分策略
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        connect_char = '&' if '?' in tid else '?'
        target_url = f"{self.host}{tid}{connect_char}page={pg}"
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                reg_rule = r'href="([^"]+-[0-9]+\.html)"[\s\S]*?src="([^"]+)"[\s\S]*?<h>([^<]+)</h>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for ep_path, pic_url, full_name in matches:
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                    
                    full_title = full_name.strip()
                    
                    # 💡 安全切分：不使用复杂的正则重切，直接使用 Python 原生的不区分大小写字符串拆分
                    # 兼容主页和其他分类页的 vs / VS 空格
                    home_team = full_title
                    remarks_text = "高清画质"
                    
                    # 尝试寻找 vs 的分割点
                    lower_title = full_title.lower()
                    if " vs " in lower_title:
                        idx = lower_title.find(" vs ")
                        home_team = full_title[:idx].strip()
                        away_team = full_title[idx+4:].strip()
                        remarks_text = f"vs {away_team}"
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': home_team,        # 标题栏：只保留主场球队名字
                        'vod_pic': pic_url,          
                        'vod_remarks': remarks_text   # 图片悬浮标签：完美浮现 “vs 客队名”
                    })
                
                result['list'] = vod_list
                result['total'] = len(vod_list)
        except:
            pass
        return result

    # 第三步修复：动态获取网页真实的标题
    def detailContent(self, ids):
        if not ids or not ids:
            return {'list': []}
        
        vid = ids  
        target_url = self.host + vid  
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 提取原网页真实的比赛全名作为播放抬头
                title_match = re.search(r'<title>([^<]+)</title>', html_content)
                real_video_name = title_match.group(1).split('|')[0].strip() if title_match else "体育精彩赛事"

                article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
                
                play_urls = []
                if article_block:
                    block_text = article_block.group(1)
                    matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([\s\S]*?)</', block_text)
                    
                    for sid, ep_name in matches:
                        clean_name = ep_name.replace('\r', '').replace('\n', '').strip()
                        play_urls.append(f"{clean_name}${sid}")
                
                if not play_urls:
                    play_urls.append(f"全场正片${vid}")
                
                return {'list': [{
                    'vod_id': vid,
                    'vod_name': real_video_name, # 抬头显示完整比赛名称
                    'vod_pic': f"{self.host}/imgs/{vid.split('-')[-1].replace('.html', '')}.png", 
                    'vod_play_from': '极速直链',    # 干净的单线路名称
                    'vod_play_url': '#'.join(play_urls)  
                }]}
        except:
            pass
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        real_m3u8_url = f"{self.host}/hls/{id}.m3u8"
        player_headers = {
            'User-Agent': self.header['User-Agent'],
            'Referer': 'https://tiktok.com'  
        }
        return {
            'parse': 0,  
            'url': real_m3u8_url,
            'header': player_headers
        }

    def searchContent(self, key, quick, pg="1"):
        return {'list': []}

    def fetch(self, url):
        return None

    def localProxy(self, param):
        return None
