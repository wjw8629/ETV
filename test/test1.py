# -*- coding: utf-8 -*-
import sys
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'FullShowSpider'

    def init(self, extend=""):
        """初始化配置，在爬虫加载时首先运行"""
        self.host = 'https://fullmatchshows.com'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.timeout = 10

    def homeContent(self, filter):
        """首页分类：定义App顶部显示的各个版块"""
        result = {'class': [], 'list': []}
        result['class'].append({'type_name': '最新', 'type_id': '/'})
        result['class'].append({'type_name': '欧冠', 'type_id': '/leagues/champions-league'})
        result['class'].append({'type_name': '英超', 'type_id': '/leagues/premier-league'})
        result['class'].append({'type_name': '西甲', 'type_id': '/leagues/la-liga'})
        result['class'].append({'type_name': '德甲', 'type_id': '/leagues/bundesliga'})
        result['class'].append({'type_name': '意甲', 'type_id': '/leagues/serie-a'})
        result['class'].append({'type_name': '法甲', 'type_id': '/leagues/ligue-1'})
        return result

    def homeVideoContent(self):
        """首页推荐视频（可选，默认返回空列表）"""
        result = {'list': []}
        return result

        def categoryContent(self, tid, pg, filter, extend):
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 0, 'total': 9999}
        
        # 拼接分类和分页 URL
        url = self.host if tid == '/' else f"{self.host}{tid}"
        if int(pg) > 1:
            url = f"{url}/page/{pg}" if url.endswith('/') else f"{url}/page/{pg}/"
            
        try:
            rsp = requests.get(url, headers=self.header, timeout=self.timeout)
            html_text = rsp.text
            
            # 使用 BeautifulSoup 解析 HTML 
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_text, 'lxml')
            
            videos = []
            # 🔍 精准锁定你提供的 HTML 特征类名：post-thumb
            thumb_divs = soup.find_all('div', class_='post-thumb')
            
            for div in thumb_divs:
                a_tag = div.find('a', class_='entry-image-link')
                img_tag = div.find('img')
                if not a_tag or not img_tag:
                    continue
                    
                # 提取基本属性
                href = a_tag.get('href', '')
                vod_id = href.replace(self.host, '') # 提取相对 ID
                img_url = img_tag.get('src', '')
                
                # 原始完整标题，例如: "Hull City vs Brentford Full Match Replay 25 Oct 2026"
                raw_title = img_tag.get('alt', '').strip()
                if not raw_title:
                    continue
                
                # 🛠️ 拆分主队与客队逻辑
                # 兼容大小写的 "vs" 或 "VS" 或 "Vs"
                lower_title = raw_title.lower()
                if 'vs' in lower_title:
                    # 找到 vs 所在的位置进行切割
                    vs_idx = lower_title.find('vs')
                    home_team = raw_title[:vs_idx].strip() # "Hull City"
                    
                    # 剩余部分，例如: "Brentford Full Match Replay 25 Oct 2026"
                    remaining = raw_title[vs_idx + 2:].strip()
                    # 进一步将多余的后缀去掉，只保留精准的客队名称
                    # 常见后缀：Full Match, Replay, Highlights
                    away_cleanup = remaining
                    for kw in ['full match', 'replay', 'highlights', 'watch']:
                        if kw in away_cleanup.lower():
                            kw_idx = away_cleanup.lower().find(kw)
                            away_cleanup = away_cleanup[:kw_idx].strip()
                            
                    away_team = away_cleanup if away_cleanup else remaining
                else:
                    # 万一标题里没找到 vs，则保底不拆分
                    home_team = "足球回放"
                    away_team = raw_title
                
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': away_team,   # 🏷️ 客队名称做主标题
                    'vod_pic': img_url,      # 🖼️ 海报图片
                    'vod_remarks': home_team # 🏷️ 主队名称做图片角落的标签
                })
                
            result['list'] = videos
            result['limit'] = len(videos)
            
        except Exception as e:
            print(f"Error in categoryContent: {e}")
            
        return result


    def detailContent(self, ids):
        """视频详情页：点击某部影片进入详情页时触发获取播放线路"""
        # ids 通常传入的是一个数组列表，比如 ['/video-id']
        result = {'list': []}
        # TODO: 稍后在这里实现抓取正文内嵌播放线路的代码
        return result

    def searchContent(self, key, quick, pg="1"):
        """全局搜索：在App内输入关键词搜索时触发"""
        result = {'list': []}
        # TODO: 稍后在这里实现搜索功能的代码
        return result

    def playerContent(self, flag, id, vipFlags):
        """播放内核解析：点击播放具体的线路URL时触发"""
        result = {}
        result["parse"] = 0  # 0代表直接原样播放，1代表使用App配置的内理解析
        result["playUrl"] = ""
        result["url"] = id   # 默认直接原路返回传入的视频链接
        result["header"] = self.header
        return result

    def localProxy(self, param):
        """本地代理服务器（可选，用于中转、M3U8解密等复杂操作）"""
        return [200, "video/MP2T", ""]
