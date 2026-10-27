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
        result['class'].append({'type_name': '意甲', 'type_id': '/cate/serie/leagues/serie-a'})
        result['class'].append({'type_name': '法甲', 'type_id': '/leagues/ligue-1'})
        
        # 🔥 关键修复点：Fongmi 在初始化首页时，会优先展示 homeContent 返回的 list
        # 如果这里是空的，海报墙就不会显示。所以在这里直接调用下面写好的海报墙抓取方法
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
                
                # 切分字符串，例如 "Hull City vs Brentford Full Match Replay..."
                parts = raw_title.split(vs_marker)
                home_team = parts[0].strip()   # 主队：Hull City
                away_part = parts[1].strip()   # 客队及后续后缀：Brentford Full Match Replay...
                
                # 进一步清洗客队：剔除 Full Match, Replay 等常见杂质关键词
                away_team = away_part
                for keyword in ['Full', 'full', 'Match', 'match', 'Replay', 'replay', 'Highlight', 'highlight']:
                    if keyword in away_team:
                        away_team = away_team.split(keyword)[0].strip()

                vod_id = href.replace(self.host, '')
                
                # 3. 按要求：图片标签(vod_name)改成主队名，标题/备注改成客队名
                result['list'].append({
                    'vod_id': vod_id,
                    'vod_name': home_team,                    # 图片标签（海报标题）为主队名
                    'vod_pic': pic,
                    'vod_remarks': f"客队: {away_team}"        # 备注显示客队名
                })
        except Exception as e:
            pass
        return result


    def categoryContent(self, tid, pg, filter, extend):
        """
        1. 分类列表页
        当在 Fongmi 点击某个分类（如英超、西甲）或翻页时触发。
        """
        result = {'list': [], 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 999}
        # TODO: 拼接带页码的分类 URL 并抓取该分类下的视频列表
        return result

    def detailContent(self, ids):
        """
        2. 详情页
        当点击海报墙上的某个视频卡片时触发，用来获取播放列表和视频简介。
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
        在全局输入关键词搜索赛事时触发。
        """
        result = {'list': []}
        return result

    def playerContent(self, flag, id, vipFlags):
        """
        4. 播放页
        点击具体的集数（如“上半场”）准备播放时触发。
        """
        result = {'parse': 0, 'playUrl': '', 'url': ''}
        result['url'] = id  
        return result
