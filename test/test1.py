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
                
                # 进一步清洗客队：通常只需要拿到第一个空格前的词，或者清理掉 Replay 等后缀
                # 这里根据目标网页特征，客队后面多带有 Full Match, Replay, 25 Oct 等
                # 我们通过常见的关键词切分，提取出干净的客队名
                away_team = away_part
                for keyword in ['Full', 'full', 'Match', 'match', 'Replay', 'replay', 'Highlight']:
                    if keyword in away_team:
                        away_team = away_team.split(keyword)[0].strip()

                vod_id = href.replace(self.host, '')
                
                # 3. 按照你的要求：图片标签(vod_name)改成主队名，而标题/备注等体现客队
                result['list'].append({
                    'vod_id': vod_id,
                    'vod_name': home_team,                    # 图片标签（海报主标题）改成：主队名
                    'vod_pic': pic,
                    'vod_remarks': f"客队: {away_team}"        # 备注或副标题显式体现：客队名
                })
        except Exception as e:
            pass
        return result


    def categoryContent(self, tid, pg, filter, extend):
        """
        1. 分类商品/视频列表页留白
        当在 Fongmi 点击某个分类（如英超、西甲）或翻页时触发。
        :param tid: 对应分类的 type_id（如 '/leagues/premier-league'）
        :param pg: 当前页码
        """
        result = {'list': [], 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 999}
        # TODO: 拼接带页码的分类 URL 并抓取该分类下的视频列表
        return result

    def detailContent(self, ids):
        """
        2. 详情页留白
        当点击海报墙上的某个视频卡片时触发，用来获取播放列表和视频简介。
        :param ids: 包含 vod_id 的列表（如 ['/hull-city-vs-brentford-.../']）
        """
        result = {'list': []}
        vod_id = ids[0]
        # TODO: 请求详情页，提取比赛简介、封面、剧集/播放线路名称、以及播放所需的链接 id
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
            'vod_play_from': '全场回放$$集锦',  # 播放源名称，用 $$ 分隔多线路
            'vod_play_url': '正半场$play_id_1#下半场$play_id_2$$高清集锦$play_id_3'  # 播放集数，线路间用 $$ 分隔，剧集内用 # 分隔
        }
        result['list'].append(vod)
        return result

    def searchContent(self, key, quick):
        """
        3. 搜索页留白
        在全局输入关键词搜索赛事时触发。
        :param key: 搜索关键词（如 'Hull City'）
        """
        result = {'list': []}
        # TODO: 请求搜索接口（通常是 self.host + '/?s=' + key），解析返回的结果列表
        return result

    def playerContent(self, flag, id, vipFlags):
        """
        4. 播放页留白
        点击具体的集数（如“上半场”）准备播放时触发，返回真正可播放的视频流媒体链接。
        :param flag: 播放源名称（即 detail 中的 vod_play_from）
        :param id: 播放任务标示（即 detail 中的 play_id）
        """
        result = {'parse': 0, 'playUrl': '', 'url': ''}
        # TODO: 如果页面内直接包含 m3u8/mp4 链接则把 parse 设为 0，直传 url；
        # 如果是第三方内嵌网盘/视频流（如 Dailymotion），则需要提取或走解析逻辑。
        result['url'] = id  # 暂时原样返回测试
        return result
