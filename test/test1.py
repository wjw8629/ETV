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
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code != 200:
                return result
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 兼容主页轮播图结构 (ticker-slider-items 内部的 a 标签)
            slider_items = soup.select('.ticker-slider-items a')
            
            # 2. 兼容其他页/分类页结构 (post-thumb 内部的 a 标签)
            normal_items = soup.select('.post-thumb a, .entry-media a')
            
            # 合并两个列表进行统一处理
            all_links = slider_items + normal_items
            
            for a_tag in all_links:
                img_tag = a_tag.find('img')
                if not img_tag:
                    continue
                    
                # 提取链接与海报地址
                vod_id = a_tag.get('href', '')
                vod_pic = img_tag.get('src', '')
                raw_title = img_tag.get('alt', '') or img_tag.get('title', '')
                
                if not raw_title or 'vs' not in raw_title.lower():
                    # 如果标题里没有 vs，直接用原标题作为备用
                    vod_name = raw_title
                    vod_remarks = "Football"
                else:
                    # 按照 "vs" 进行切分，转换为小写处理避免大小写不一致
                    parts = raw_title.lower().split('vs')
                    home_team = parts[0].strip().title() # 变成首字母大写
                    
                    # 后面部分可能带有 "Full Match Replay..."，清理掉
                    away_part = parts[1].split('full')[0].split('replay')[0].strip()
                    away_team = away_part.title()
                    
                    # 核心需求：海报标签(remarks)显示主队，标题(name)显示客队名称
                    vod_remarks = home_team  # 标签显示主队
                    vod_name = away_team     # 标题显示客队
                
                # 过滤重复项并添加到结果列表中
                vod_item = {
                    'vod_id': vod_id,
                    'vod_name': vod_name,
                    'vod_pic': vod_pic,
                    'vod_remarks': vod_remarks
                }
                if vod_item not in result['list']:
                    result['list'].append(vod_item)
                    
        except Exception as e:
            print(f"解析出错: {e}")
            
        return result
