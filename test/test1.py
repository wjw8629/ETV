# -*- coding: utf-8 -*-
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'FullShowSpider'

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
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    # 💡 【核心拦截改动】：如果标题里不包含 "vs"，直接证明是导航菜单（如Home）或杂质广告，当场丢弃过滤
                    if "vs" not in lower_title:
                        continue  # 跳过当前循环，不抓取、不打包
                        
                    # 走到这里，说明百分之百是一场带有 "vs" 的正规球赛
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    ep_path = full_url.replace(self.host, "")
                    
                    # 完美执行你的主客队名字对调切分
                    idx = lower_title.find("vs")
                    home_team = full_title[:idx].strip().rstrip('-').strip()
                    away_team = full_title[idx+2:].strip()
                    
                    # 精简去掉客队末尾长长的废话后缀（如 full match replay）
                    if " full match" in away_team.lower():
                        f_idx = away_team.lower().find(" full match")
                        away_team = away_team[:f_idx].strip()
                    if " replay" in away_team.lower():
                        r_idx = away_team.lower().find(" replay")
                        away_team = away_team[:r_idx].strip()
                        
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': f"vs {away_team}", # 标题大字：显示 “vs 客队名”
                        'vod_pic': pic_url,          
                        'vod_remarks': home_team       # 海报标签：显示 “主场球队名”
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