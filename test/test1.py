# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'FullShowSpider'

    def init(self, extend=""):
        # ⚠️ 确保主域名完全精准，不要带末尾的斜杠
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
        
        home_videos = self.homeVideoContent()
        result['list'] = home_videos.get('list', [])
        return result

    def homeVideoContent(self):
        result = {'list': []}
        try:
            response = requests.get(self.host, headers=self.header, timeout=self.timeout)
            if response.status_code != 200:
                return result
            soup = BeautifulSoup(response.text, 'html.parser')
            result['list'] = self.parseVideoList(soup)
        except Exception as e:
            pass
        return result

    def categoryContent(self, tid, pg, filter, extend):
        """
        1. 分类列表页核心修复点
        当在 Fongmi 点击某个分类（如英超、西甲）或翻页时触发。
        """
        result = {'list': [], 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 999}
        try:
            # 兼容首页分类和多页结构，全网一般翻页格式为 /page/2/ 或 /leagues/premier-league/page/2/
            url = self.host + tid
            if int(pg) > 1:
                # 拼接翻页链接
                if url.endswith('/'):
                    url = f"{url}page/{pg}/"
                else:
                    url = f"{url}/page/{pg}/"

            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code != 200:
                return result
                
            soup = BeautifulSoup(response.text, 'html.parser')
            result['list'] = self.parseVideoList(soup)
        except Exception as e:
            pass
        return result

    def parseVideoList(self, soup):
        """
        公共数据解析抽取方法（包含过滤非VS链接、主客队名称重置逻辑）
        """
        video_list = []
        matches = soup.find_all('a', class_='entry-image-link')
        
        for match in matches:
            img_tag = match.find('img')
            if not img_tag:
                continue
            
            raw_title = img_tag.get('alt', '').strip()
            href = match.get('href', '')
            pic = img_tag.get('src', '')
            
            if not raw_title or not href:
                continue

            # 1. 统一转换大小写并判断是否包含 vs，没有则不抓取
            lower_title = raw_title.lower()
            if 'vs' not in lower_title:
                continue

            # 2. 找到实际的 vs 分隔符并切分出主队和客队
            vs_marker = "vs"
            if "VS" in raw_title:
                vs_marker = "VS"
            elif "Vs" in raw_title:
                vs_marker = "Vs"
            
            parts = raw_title.split(vs_marker)
            home_team = parts[0].strip()   # 主队
            away_part = parts[1].strip()   # 客队及后续后缀
            
            # 进一步清洗客队：剔除 Full Match, Replay 等常见杂质关键词
            away_team = away_part
            for keyword in ['Full', 'full', 'Match', 'match', 'Replay', 'replay', 'Highlight', 'highlight', '&amp;']:
                if keyword in away_team:
                    away_team = away_team.split(keyword)[0].strip()

            vod_id = href.replace(self.host, '')
            
            # 3. 按修改后的逻辑：图片标签（vod_name）显式客队，备注（vod_remarks）显式主队
            video_list.append({
                'vod_id': vod_id,
                'vod_name': f"vs {away_team}",                    # 标题：vs 客队名
                'vod_pic': pic,
                'vod_remarks': home_team                        # 备注：主队名
            })
        return video_list

    def detailContent(self, ids):
        """
        2. 详情页
        """
        result = {'list': []}
        vod_id = ids[0]
        vod = {
            'vod_id': vod_id,
            'vod_name': '比赛名称',
            'vod_pic': '',
            'type_name': '足球赛事',
            'vod_year': '2026',
            'vod_area': '欧洲',
            'vod_actor': '',
            'vod_director': '',
            'vod_content': '赛事内容简介',
            'vod_play_from': '全场回放$$集锦',  
            'vod_play_url': '正半场$play_id_1#下半场$play_id_2$$高清集锦$play_id_3'  
        }
        result['list'].append(vod)
        return result

    def searchContent(self, key, quick):
        """
        3. 搜索页
        """
        result = {'list': []}
        return result

    def playerContent(self, flag, id, vipFlags):
        """
        4. 播放页
        """
        result = {'parse': 0, 'playUrl': '', 'url': ''}
        result['url'] = id  
        return result
