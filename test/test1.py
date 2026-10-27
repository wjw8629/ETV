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


            # 2. 第二步：请求新网站分类，字数压缩排版 + 图片 CDN 瘦身（全面提升 FongMi 跑图速度）
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        
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
                
                reg_rule = r'src="([^"]+)"[\s\S]*?itemprop="headline"[\s\S]*?href="([^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for pic_url, full_url, full_name in matches:
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    if "vs" not in lower_title:
                        continue
                        
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    # 🚀【核心改良：图片云端强力瘦身】
                    if "?" in pic_url:
                        raw_pic = pic_url.split("?")[0]
                    else:
                        raw_pic = pic_url
                    # 压缩到 320px 宽，剥离所有图片多余信息，画质调整到 70%，极大降低内存占用并秒开海报
                    pic_url = f"{raw_pic}?w=320&strip=all&quality=70&ssl=1"
                        
                    ep_path = full_url.replace(self.host, "")
                    
                    clean_title = full_title
                    for word in ["full match replay", "full match", "replay", "highlights"]:
                        if word in clean_title.lower():
                            w_idx = clean_title.lower().find(word)
                            clean_title = clean_title[:w_idx].strip()
                    
                    display_date = ""
                    date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]+)\s+\d{4}', clean_title)
                    if date_match:
                        display_date = date_match.group(1).strip()
                        full_date_str = re.search(r'(\d{1,2}\s+[a-zA-Z]+\s+\d{4})', clean_title).group(1)
                        clean_title = clean_title.replace(full_date_str, "").strip()
                    
                    vs_match = re.search(r'\s+[vV][sS]\s+', clean_title)
                    if vs_match:
                        vs_str = vs_match.group(0)
                        parts = clean_title.split(vs_str)
                        home_team = parts[0].strip().rstrip('-').strip()
                        away_team = parts[1].strip().lstrip('-').strip()
                    else:
                        idx = clean_title.lower().find("vs")
                        home_team = clean_title[:idx].strip().rstrip('-').strip()
                        away_team = clean_title[idx+2:].strip().lstrip('-').strip()
                    
                    home_team = home_team.rstrip('-').strip()
                    away_team = away_team.rstrip('-').strip()
                    
                    replace_dict = {
                        "Manchester United": "Man Utd",
                        "Manchester City": "Man City",
                        "Tottenham Hotspur": "Tottenham",
                        "Atletico Madrid": "Atletico",
                        "Real Madrid": "R.Madrid",
                        "Bayern Munich": "Bayern",
                        "Borussia Dortmund": "Dortmund",
                        "Bayer Leverkusen": "Leverkusen",
                        "Paris Saint-Germain": "PSG",
                        "Saint-Germain": "PSG"
                    }
                    for long_name, short_name in replace_dict.items():
                        if long_name in home_team:
                            home_team = home_team.replace(long_name, short_name)
                        if long_name in away_team:
                            away_team = away_team.replace(long_name, short_name)
                    
                    if len(away_team) > 12:
                        away_team = away_team[:11] + "."
                    
                    tag_remark = home_team                        
                    title_name = f"{away_team} {display_date}".strip() 
                    
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': title_name,       
                        'vod_pic': pic_url,           
                        'vod_remarks': tag_remark     
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