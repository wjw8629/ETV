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

        # 用纯正则安全重写的一级列表页
    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg)
        except:
            pg = 1
            
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        
        # 拼接分类和分页 URL
        url = self.host if tid == '/' else f"{self.host}{tid}"
        if pg > 1:
            url = f"{url}/page/{pg}" if url.endswith('/') else f"{url}/page/{pg}/"
            
        try:
            import requests
            import re
            
            # 发起请求，verify=False 规避盒子老旧系统证书报错
            r = requests.get(url, headers=self.header, timeout=self.timeout, verify=False)
            if r.status_code == 200:
                html_content = r.text
                
                # 🔍 精准匹配你在 HTML 里面给我的 post-thumb 链接、图片、以及 alt 完整标题
                reg_rule = r'class="post-thumb[^"]*">.*?href="([^"]+)"[^>]*><img[^>]*src="([^"]+)"[^>]*alt="([^"]+)"'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for href, pic_url, full_title in matches:
                    # 转换相对路径ID
                    vod_id = href.replace(self.host, '')
                    
                    full_name = full_title.strip()
                    lower_title = full_name.lower()
                    
                    # 🛠️ 严格按照你的指示切分：主队做标签（remarks），客队做标题（name）
                    if "vs" in lower_title:
                        idx = lower_title.find("vs")
                        # 切出主队名称
                        home_team = full_name[:idx].strip().rstrip('-').strip()
                        
                        # 切出剩余部分，并清洗多余后缀
                        remaining = full_name[idx+2:].strip().lstrip('-').strip()
                        away_cleanup = remaining
                        for kw in ['full match', 'replay', 'highlights', 'watch', '2026']:
                            if kw in away_cleanup.lower():
                                kw_idx = away_cleanup.lower().find(kw)
                                away_cleanup = away_cleanup[:kw_idx].strip()
                                
                        away_team = away_cleanup if away_cleanup else remaining
                    else:
                        # 保底逻辑
                        home_team = "足球赛事"
                        away_team = full_name
                        
                    vod_list.append({
                        'vod_id': vod_id,            
                        'vod_name': away_team,     # 🏷️ 客队名称做主标题
                        'vod_pic': pic_url,          
                        'vod_remarks': home_team   # 🏷️ 主队名称做图片角落的标签
                    })

                result['list'] = vod_list
                result['total'] = len(vod_list)
        except Exception as e:
            # 即使报错也绝不让App闪退，而是把错误打印在电视的第一条卡片上
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
