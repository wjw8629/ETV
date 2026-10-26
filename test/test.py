# -*- coding: utf-8 -*-
import re
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'SoccerFullSpider'

    def init(self, extend=""):
        # ⚠️ 确保主域名完全精准，不要带末尾的斜杠
        self.host = 'https://soccerfull.net'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.timeout = 10

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

    # 🔥 核心修正：去除一切可能导致崩溃的复杂切分，先确保海报原样刷出来
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        
        connect_char = '&' if '?' in tid else '?'
        target_url = f"{self.host}{tid}{connect_char}page={pg}"
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 🔍 这里使用了最稳妥的全包容正则，匹配你发给我的原生 <h2> 和 <h3> 结构
                reg_rule = r'href="([^"]+-[0-9]+\.html)"[\s\S]*?src="([^"]+)"[\s\S]*?<(?:h2|h3)>([^<]+)</(?:h2|h3)>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for ep_path, pic_url, full_name in matches:
                                    vod_list = []
                for ep_path, pic_url, full_name in matches:
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                    
                    full_title = full_name.strip()
                    
                    # 💡 【核心安全切分逻辑】
                    # 使用不区分大小写的正则分割，最多只切一刀
                    split_title = re.split(r'\s+[vV][sS]\s+', full_title, maxsplit=1)
                    
                    # ⚠️ 加上铁律保底：如果切成功了（有主队有客队），才进行切分展示
                    if len(split_title) == 2:
                        home_team = split_title[0].strip()   # 左边是主队名
                        away_team = split_title[1].strip()   # 右边是客队名
                        remarks_text = f"vs {away_team}"     # 角标栏显示：vs 客队
                    else:
                        # 🔒 保底防御：如果没有找到 vs 字样，直接显示网页原名，右下角写固定文本
                        home_team = full_title
                        remarks_text = "高清赛事"
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': home_team,        # 标题栏：只显示主场球队名字
                        'vod_pic': pic_url,          
                        'vod_remarks': remarks_text   # 图片悬浮标签：完美浮现 “vs 客队名”
                    })
                
                result['list'] = vod_list
                result['total'] = len(vod_list)
        except:
            pass
        return result

    # 保持后续函数空壳占位，不干扰前面的编译运行
    def detailContent(self, ids):
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        return {'parse': 0, 'url': ''}

    def searchContent(self, key, quick, pg="1"):
        return {'list': []}

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass
