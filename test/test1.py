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


        # 2. 第二步：请求新网站分类，纯文本文字排版重组，破除 App 竖屏框硬伤
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
                        
                    # 💡 图片恢复原样，不做任何比例和参数修改
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    ep_path = full_url.replace(self.host, "")
                    
                    # 1. 精准斩断客队末尾长长的 full match 废话后缀，防止干扰日期提取
                    clean_title = full_title
                    for word in ["full match replay", "full match", "replay", "highlights"]:
                        if word in clean_title.lower():
                            w_idx = clean_title.lower().find(word)
                            clean_title = clean_title[:w_idx].strip()
                    
                    # 2. 提取原生日期并清洗为“月日”（例如将 "25 Oct 2026" 提炼为 "25 Oct"）
                    display_date = ""
                    # 匹配类似 25 Oct 2026 或 25 October 2026
                    date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]+)\s+\d{4}', clean_title)
                    if date_match:
                        display_date = date_match.group(1).strip()  # 只要 “日 月”，干掉年份
                        # 从干净标题里把整段日期（含年份）抹掉
                        full_date_str = re.search(r'(\d{1,2}\s+[a-zA-Z]+\s+\d{4})', clean_title).group(1)
                        clean_title = clean_title.replace(full_date_str, "").strip()
                    
                    # 3. 用不区分大小写的 "vs" 拆分主队与客队
                    vs_match = re.search(r'\s+[vV][sS]\s+', clean_title)
                    if vs_match:
                        vs_str = vs_match.group(0)
                        parts = clean_title.split(vs_str)
                        home_team = parts[0].strip().rstrip('-').strip()
                        away_team = parts[1].strip().lstrip('-').strip()
                    else:
                        # 兜底容错：如果正则拆失败了，用原有逻辑定位
                        idx = clean_title.lower().find("vs")
                        home_team = clean_title[:idx].strip().rstrip('-').strip()
                        away_team = clean_title[idx+2:].strip().lstrip('-').strip()
                    
                    # 4. 再次清洗主客队末尾残留的连字符
                    home_team = home_team.rstrip('-').strip()
                    away_team = away_team.rstrip('-').strip()
                    
                    # 5. 按照您的新规组装排版
                    # 标签：只显示主队
                    tag_remark = home_team
                    # 标题：客队 + 月日
                    title_name = f"{away_team} {display_date}".strip()
                    
                    vod_list.append({
                        'vod_id': ep_path,            
                        'vod_name': title_name,       # 下方大字标题栏：客队 25 Oct
                        'vod_pic': pic_url,           # 恢复原始状态的图片链接
                        'vod_remarks': tag_remark     # 海报悬浮角标栏：主队
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