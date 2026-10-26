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
                    
                    # 💡 【全模糊安全切分】
                    # 先统一转成小写来找位置，彻底无视大小写和两边到底有几个空格或符号
                    lower_title = full_title.lower()
                    
                    if "vs" in lower_title:
                        # 找到 vs 在字符串里的起始位置
                        idx = lower_title.find("vs")
                        # 左边切出主队，刮干净两端可能残留的空格或横线
                        home_team = full_title[:idx].strip().rstrip('-').strip()
                        # 右边切出客队，跳过 v 和 s 两个字母，同样刮干净多余符号
                        away_team = full_title[idx+2:].strip().lstrip('-').strip()
                        
                        remarks_text = f"vs {away_team}"
                    else:
                        # 保底：万一真的没有 vs，原样输出
                        home_team = full_title
                        remarks_text = "高清赛事"
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': remarks_text,        # 标题栏：只保留主场球队
                        'vod_pic': pic_url,          
                        'vod_remarks': home_team   # 角标栏：动态悬浮显示 “vs 客队名”
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
