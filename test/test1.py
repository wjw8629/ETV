# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'FullShowSpider'

    def init(self, extend=""):
        self.host = 'https://fullmatchshows.com'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.timeout = 10

    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        result['class'].append({'type_name': '最新', 'type_id': '/'})
        result['class'].append({'type_name': '欧冠', 'type_id': '/leagues/champions-league'})
        result['class'].append({'type_name': '英超', 'type_id': '/leagues/premier-league'})
        result['class'].append({'type_name': '西甲', 'type_id': '/leagues/la-liga'})
        result['class'].append({'type_name': '德甲', 'type_id': '/leagues/bundesliga'})
        result['class'].append({'type_name': '意甲', 'type_id': '/leagues/serie-a'})
        result['class'].append({'type_name': '法甲', 'type_id': '/leagues/ligue-1'})
        return result

        def categoryPage(self, tid, pg, filter):
        # 拼接分类与页码 URL
        url = self.host + tid
        if pg > 1:
            url = f"{url}/page/{pg}"
            
        result = {'list': []}
        try:
            # 升级反爬 Headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': self.host,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return result
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 精准定位包含海报的区域（同时兼容你提供的主页和其它页标签结构）
            items = soup.select('.post-thumb a, .entry-media a, .ticker-slider-items a')
            
            for a_tag in items:
                img_tag = a_tag.find('img')
                if not img_tag:
                    continue
                    
                vod_id = a_tag.get('href', '')
                # 优先读取 src，若有懒加载则读取 data-src 兜底
                vod_pic = img_tag.get('src', '') or img_tag.get('data-src', '')
                raw_title = img_tag.get('alt', '') or img_tag.get('title', '')
                
                if not vod_id or not vod_pic or not raw_title:
                    continue
                    
                # 将文本中的 " vs " 作为切分标志
                if ' vs ' in raw_title:
                    parts = raw_title.split(' vs ')
                    home_team = parts[0].strip()  # 提取主队名称
                    
                    # 此时 parts[1] 形如 "Brentford Full Match Replay 25 Oct 2026"
                    # 我们需要将其后面的多余非队伍文本清洗掉
                    away_part = parts[1]
                    for keyword in ['Full', 'full', 'Match', 'match', 'Replay', 'replay', '202']:
                        if keyword in away_part:
                            away_part = away_part.split(keyword)[0]
                    
                    away_team = away_part.strip()  # 提取干净的客队名称
                    
                    # 严格执行要求：海报标签显示主队，标题显示客队名称
                    vod_remarks = home_team
                    vod_name = away_team
                else:
                    # 兜底清洗逻辑
                    vod_name = raw_title.split('Full')[0].split('full')[0].strip()
                    vod_remarks = "Football"
                
                vod_item = {
                    'vod_id': vod_id,
                    'vod_name': vod_name,
                    'vod_pic': vod_pic,
                    'vod_remarks': vod_remarks
                }
                
                # 过滤可能存在的重复节点
                if vod_item not in result['list']:
                    result['list'].append(vod_item)
                    
        except Exception as e:
            print(f"解析出错: {e}")
            
        return result

