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

        # 2. 第二步：请求新网站分类，实时缩放宽幅海报，破除 App 竖屏框切队徽的硬伤
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        
        # 兼容 WordPress 的标准翻页路由
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
                
                # 精准正则：捞取海报、路径、比赛全名
                reg_rule = r'src="([^"]+)"[\s\S]*?itemprop="headline"[\s\S]*?href="([^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for pic_url, full_url, full_name in matches:
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    # 🔥 拦截过滤：如果标题里不包含 "vs"，说明是 Home 菜单或垃圾推广，直接过滤丢弃
                    if "vs" not in lower_title:
                        continue
                        
                    # 💡 【核心图片缩放突破点】
                    # 如果原网站的图片是相对路径，先补全它
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                    
                    # 🚀 宽度对齐优化：剥离原有的高宽裁剪参数，强制指定宽度为 500 像素，高度自适应
                    if "?resize=" in pic_url:
                        pic_url = pic_url.split("?resize=")[0]
                    elif "?w=" in pic_url:
                        pic_url = pic_url.split("?w=")[0]
                    elif "?" in pic_url:
                        pic_url = pic_url.split("?")[0]
                        
                    # 注入 w=500 参数：强制让图片以 500px 宽度对齐缩放，不限制高度，从而让宽度完全完整显示
                    pic_url = pic_url + "?w=500&ssl=1"
                        
                    ep_path = full_url.replace(self.host, "")
                    
                    # 拆分主客队
                    idx = lower_title.find("vs")
                    home_team = full_title[:idx].strip().rstrip('-').strip()
                    away_team = full_title[idx+2:].strip()
                    
                    # 截出原网站原生日期（例如 25 Oct 2026）
                    display_date = "近期赛事"
                    date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]{3}\s+\d{4})', away_team)
                    if date_match:
                        display_date = date_match.group(1)
                        # 将日期从客队名字里抹掉，防止对阵太长被截断
                        away_team = away_team.replace(date_match.group(1), "").strip()
                    
                    # 斩断客队末尾长长的 full match 废话后缀
                    for word in ["full match replay", "full match", "replay", "highlights"]:
                        if word in away_team.lower():
                            w_idx = away_team.lower().find(word)
                            away_team = away_team[:w_idx].strip()
                    away_team = away_team.rstrip('-').strip()
                    
                    # 组装对阵大牌
                    match_vs_text = f"{home_team} VS {away_team}"
                    
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': display_date,     # 下方大字标题栏：显示干净的原生日期（25 Oct 2026）
                        'vod_pic': pic_url,           # 核心：已经执行宽度自适应、绝对不切队徽的安全图
                        'vod_remarks': match_vs_text  # 海报悬浮角标栏：显示完整的对阵 [主队 VS 客队]
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