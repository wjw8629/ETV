# -*- coding: utf-8 -*-
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'SoccerFullSpider'

    def init(self, extend=""):
        # ⚠️ 确保主域名完全精准，不要带末尾的斜杠
        self.host = 'https://fullmatchshows.com/'  
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
        result['class'].append({'type_name': '法甲', 'type_id': 'leagues/ligue-1'})
        return result


    # ==========================================
    # 以下全为空壳保底函数，确保新站第一步顺利编译通过
    # ==========================================
    def homeVideoContent(self):
        return {}

        # 核心：请求新网站对应的标签网址，精准洗出全新排版的视频封面墙
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        # 初始化 Fongmi 标准数据结构（允许翻页）
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        
        # 拼接带页码的分页网址（WordPress 通用分页路由为 /page/页码）
        if pg > 1:
            target_url = f"{self.host}{tid}page/{pg}/" if tid.endswith("/") else f"{self.host}{tid}/page/{pg}/"
        else:
            target_url = f"{self.host}{tid}"
            
        try:
            import requests
            import re
            
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 🔍 新站独家精密正则：完美匹配图片直链、跳转路径以及 headline 标题
                # 结构：src="图片" ... itemprop="headline"> <a href="路径" ... >比赛全名</a>
                reg_rule = r'src="([^"]+)"[\s\S]*?itemprop="headline"[\s\S]*?href="([^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for pic_url, full_url, full_name in matches:
                    # 将完整的 https 网址剥离为相对路径，方便后续详情页统一接收
                    ep_path = full_url.replace(self.host, "")
                    
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    # 默认保底值
                    home_team = full_title
                    remarks_text = "高清赛事"
                    
                    # 💡 完美平移你上一站最满意的主客队对调风格！
                    if "vs" in lower_title:
                        idx = lower_title.find("vs")
                        home_team = full_title[:idx].strip().rstrip('-').strip()
                        away_team = full_title[idx+2:].strip()
                        # 去掉可能残留在客队末尾的废话后缀
                        if " full match" in away_team.lower():
                            f_idx = away_team.lower().find(" full match")
                            away_team = away_team[:f_idx].strip()
                            
                        remarks_text = home_team
                        display_name = f"vs {away_team}"
                    else:
                        display_name = full_title
                        
                    vod_list.append({
                        'vod_id': ep_path,            # 把长英文路径传给下一步详情页
                        'vod_name': display_name,     # 标题栏大字：显示 “vs 客队名”
                        'vod_pic': pic_url,           # 封面海报图直链
                        'vod_remarks': remarks_text   # 右下角标签：显示 “主场球队名”
                    })
                
                result['list'] = vod_list
                result['total'] = len(vod_list)
        except:
            pass
            
        return result


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