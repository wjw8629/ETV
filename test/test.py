# -*- coding: utf-8 -*-
import re
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'SoccerFullSpider'

    def init(self, extend=""):
        # 全局站点主域名配置
        self.host = 'https://soccerfull.net'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.timeout = 10

    # 1. 第一步：下发分类标签
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

    # 2. 第二步：分类页面列表加载（完美兼容 h2/h3、多空格换行，并执行主客队调换视觉样式）
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        connect_char = '&' if '?' in tid else '?'
        target_url = f"{self.host}{tid}{connect_char}page={pg}"
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                reg_rule = r'href="([^"]+-[0-9]+\.html)"[\s\S]*?src="([^"]+)"[\s\S]*?<(?:h2|h3)>([^<]+)</(?:h2|h3)>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for ep_path, pic_url, full_name in matches:
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                    
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    display_name = full_title
                    remarks_text = "高清赛事"
                    
                    if "vs" in lower_title:
                        idx = lower_title.find("vs")
                        home_team = full_title[:idx].strip().rstrip('-').strip()
                        away_team = full_title[idx+2:].strip().lstrip('-').strip()
                        
                        # 完美保持你最满意的专属故意设计版式
                        remarks_text = home_team
                        display_name = f"vs {away_team}"
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': home_team,        # 标题大字大字显示：“主场球队名”
                        'vod_pic': pic_url,          
                        'vod_remarks': display_name   # 角标贴片浮现：“vs 客队描述”
                    })
                
                result['list'] = vod_list
                result['total'] = len(vod_list)
        except:
            pass
        return result

    # 3. 第三步：用户点击海报封面进入详情页，智能识别路径，洗净换行符提取 Full Match 选集
    def detailContent(self, ids):
        if not ids or not ids:
            return {'list': []}
        
        vid = ids  
        if vid.startswith("/"):
            target_url = self.host + vid
        elif ".html" in vid:
            target_url = self.host + "/" + vid if not vid.startswith("/") else self.host + vid
        else:
            target_url = f"{self.host}/{vid}.html"
            
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                title_match = re.search(r'<title>([^<]+)</title>', html_content)
                real_video_name = title_match.group(1).split('|').strip() if title_match else "体育精彩赛事"

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
                    'vod_name': real_video_name, # 抬头精准显示比赛的真实对阵全称
                    'vod_pic': f"{self.host}/imgs/{vid.split('-')[-1].replace('.html', '')}.png", 
                    'vod_play_from': '极速直链',   
                    'vod_play_url': '#'.join(play_urls)  
                }]}
        except:
            pass
        return {'list': []}

    # 4. 第五步：电视端全局输入框精准搜索功能实现
    def searchContent(self, key, quick, pg="1"):
        result = {'list': []}
        clean_key = key.strip().lower().replace(' ', '-')
        search_url = f"{self.host}/search/{clean_key}"
        
        try:
            r = requests.get(search_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                reg_rule = r'href="([^"]+-[0-9]+\.html)"[\s\S]*?src="([^"]+)"[\s\S]*?<(?:h2|h3)>([^<]+)</(?:h2|h3)>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for ep_path, pic_url, full_name in matches:
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                    
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    display_name = full_title
                    remarks_text = "搜索结果"
                    
                    if "vs" in lower_title:
                        idx = lower_title.find("vs")
                        home_team = full_title[:idx].strip().rstrip('-').strip()
                        away_team = full_title[idx+2:].strip().lstrip('-').strip()
                        
                        remarks_text = home_team
                        display_name = f"vs {away_team}"
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': home_team,        # 保持统一设计：大字显主队
                        'vod_pic': pic_url,          
                        'vod_remarks': display_name   # 悬浮角标显客队
                    })
                result['list'] = vod_list
        except:
            pass
        return result

    # 5. 第四步大结局：点击按钮瞬间完成直链派发，带上伪装 Headers 让电视硬解秒播
    def playerContent(self, flag, id, vipFlags):
        real_m3u8_url = f"{self.host}/hls/{id}.m3u8"
        player_headers = {
            'User-Agent': self.header['User-Agent'],
            'Referer': 'https://tiktok.com'  # 突破字节云安全防盗链的关键密钥
        }
        return {
            'parse': 0,  
            'url': real_m3u8_url,
            'header': player_headers
        }

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass
