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

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 0, 'total': 9999}
        
        url = self.host if tid == '/' else f"{self.host}{tid}"
        if int(pg) > 1:
            url = f"{url}/page/{pg}" if url.endswith('/') else f"{url}/page/{pg}/"
            
        try:
            # 导入标准 requests，增加 verify=False 防止盒子因证书问题报错
            import requests
            rsp = requests.get(url, headers=self.header, timeout=self.timeout, verify=False)
            html_text = rsp.text
            
            from bs4 import BeautifulSoup
            # 💡 安全修正：将 'lxml' 换成 Python 自带、完全通用的 'html.parser'
            soup = BeautifulSoup(html_text, 'html.parser')
            
            videos = []
            thumb_divs = soup.find_all('div', class_='post-thumb')
            
            for div in thumb_divs:
                a_tag = div.find('a', class_='entry-image-link')
                img_tag = div.find('img')
                if not a_tag or not img_tag:
                    continue
                    
                href = a_tag.get('href', '')
                vod_id = href.replace(self.host, '')
                img_url = img_tag.get('src', '')
                
                raw_title = img_tag.get('alt', '')
                if not raw_title:
                    raw_title = a_tag.get('title', '')
                raw_title = raw_title.strip()
                
                if not raw_title:
                    continue
                
                # 🛠️ 拆分主队与客队
                lower_title = raw_title.lower()
                if 'vs' in lower_title:
                    vs_idx = lower_title.find('vs')
                    home_team = raw_title[:vs_idx].strip()
                    
                    remaining = raw_title[vs_idx + 2:].strip()
                    away_cleanup = remaining
                    # 清理多余后缀，只保留客队名称
                    for kw in ['full match', 'replay', 'highlights', 'watch', '2026']:
                        if kw in away_cleanup.lower():
                            kw_idx = away_cleanup.lower().find(kw)
                            away_cleanup = away_cleanup[:kw_idx].strip()
                            
                    away_team = away_cleanup if away_cleanup else remaining
                else:
                    home_team = "足球回放"
                    away_team = raw_title
                
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': away_team,   # 客队做标题
                    'vod_pic': img_url,      # 海报
                    'vod_remarks': home_team # 主队做标签
                })
                
            result['list'] = videos
            result['limit'] = len(videos)
            
        except Exception as e:
            # 万一发生异常，把错误信息作为一条视频的标题返回，方便在电视屏幕上直接看到报错原因
            result['list'] = [{
                'vod_id': 'error',
                'vod_name': f"解析捕获错误: {str(e)}",
                'vod_pic': '',
                'vod_remarks': '请检查'
            }]
            
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
