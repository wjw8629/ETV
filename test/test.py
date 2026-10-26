# -*- coding: utf-8 -*-
import re
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'SoccerFullSpider'

    def init(self, extend=""):
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

    # 🔥 第二步调校：在这里执行“主队/客队”双文本切分逻辑
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
                    
                    # 💡 核心切分：利用不区分大小写的正则，把“主队 vs 客队”拆开
                    split_match = re.split(r'\s+[vV][sS]\s+', full_title, maxsplit=1)
                    if len(split_match) == 2:
                        home_team = split_match[0].strip()  # 主队名
                        away_team = split_match[1].strip()  # 客队名
                        remarks_text = f"vs {away_team}"    # 角标显示：vs 客队名
                    else:
                        home_team = full_title              # 保底：如果没有vs，显示全称
                        remarks_text = "高清画质"
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': home_team,        # 标题栏：只显示主队，永远是主场球队
                        'vod_pic': pic_url,          
                        'vod_remarks': remarks_text   # 角标栏：精致悬浮显示“vs 客队名”
                    })
                
                result['list'] = vod_list
                result['total'] = len(vod_list)
        except:
            pass
        return result

    # 🔥 第三步调校：在这里彻底改掉“赛事全场高清”的死板废话
    def detailContent(self, ids):
        if not ids or not ids:
            return {'list': []}
        
        vid = ids  
        target_url = self.host + vid  
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 顺手把网页里的完整比赛名字捞出来，作为详情页和播放器上方的真实抬头
                # 匹配源码里的 <title>标签或者通过路径转换，这里直接截取网页的真实 <h1> 或 <title> 最精准
                title_match = re.search(r'<title>([^<]+)</title>', html_content)
                real_video_name = title_match.group(1).split('-')[0].strip() if title_match else "体育精彩赛事"

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
                    'vod_name': real_video_name, # 💡 核心修改：变成真正的比赛名字！让你看的时候一目了然
                    'vod_pic': f"{self.host}/imgs/{vid.split('-')[-1].replace('.html', '')}.png", 
                    'vod_play_from': '极速直链',    # 💡 线路名称改得极简，防止多余的 flag 干扰
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
