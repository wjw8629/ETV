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
                    
                    # 铁律拦截：如果标题里不包含 "vs"，直接过滤掉Home或垃圾广告
                    if "vs" not in lower_title:
                        continue
                        
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    ep_path = full_url.replace(self.host, "")
                    
                    # 1. 🔍 拆分出主队
                    idx = lower_title.find("vs")
                    home_team = full_title[:idx].strip().rstrip('-').strip()
                    away_team = full_title[idx+2:].strip()
                    
                    # 2. 🔍 智能切出原网站自带的原生时间后缀（例如 25 Oct 2026）
                    # 新网站的标题非常有规律，最后 11 个字符通常就是类似 "25 Oct 2026"
                    display_date = "近期赛事"
                    # 匹配形如 "25 Oct 2026" 或 "5 Oct 2026" 的原生时间后缀
                    date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]{3}\s+\d{4})', away_team)
                    if date_match:
                        display_date = date_match.group(1) # 直接白嫖原网站的原生日期，如 25 Oct 2026
                    
                    # 3. 🔍 清洗客队名字，把客队末尾所有的 full match 等废话和刚刚切出来的日期全部斩断
                    if " full" in away_team.lower():
                        f_idx = away_team.lower().find(" full")
                        away_team = away_team[:f_idx].strip()
                    else:
                        # 如果没有 full 关键字，就把刚才匹配到的日期从客队名字里抹掉，防止客队名字太长
                        if date_match:
                            away_team = away_team.replace(date_match.group(1), "").strip().rstrip('-').strip()
                        
                    # 4. 🎨 终极排版打包
                    match_vs_text = f"{home_team} VS {away_team}" # 拼接出标准的对阵大牌 [皇家马德里 VS 巴塞罗那]
                    
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': display_date,     # ⬇️ 大字标题栏：直接显示原生的比赛日期（如 25 Oct 2026）
                        'vod_pic': pic_url,          
                        'vod_remarks': match_vs_text  # ⬆️ 海报悬浮标签：显示霸气的完整对阵 [主队 VS 客队]
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