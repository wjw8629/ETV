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

    # 2. 第二步：请求新网站分类，标签改回日期，标题为 7格对齐压缩的主客队对阵
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
                
                # 💡【核心算法：将任意球队名字完美压缩进固定 7 格宽度】
                def format_team_name(team_name):
                    team_name = team_name.strip()
                    # 用空格将可能存在的多个单词切开
                    words = [w for w in team_name.split(' ') if w]
                    
                    if len(words) >= 2:
                        # 多单词：前两个单词各取 3 个字母，中间加 1 个空格，合起来正好 7 个格子
                        part1 = words[0][:3]
                        part2 = words[1][:3]
                        res = f"{part1} {part2}"
                    else:
                        # 单单词：直接截取前 7 个字母
                        res = team_name[:7]
                    
                    # 补齐机制：如果名字太短，用空格往后补满 7 个格子，确保对齐
                    return res.ljust(7)

                vod_list = []
                for pic_url, full_url, full_name in matches:
                    full_title = full_name.strip()
                    lower_title = full_title.lower()
                    
                    # 🔥 拦截过滤：如果标题里不包含 "vs"，说明是垃圾内容，直接过滤丢弃
                    if "vs" not in lower_title:
                        continue
                        
                    # 💡 图片部分回归最初始抓取逻辑，不做任何裁剪与尺寸加工
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    ep_path = full_url.replace(self.host, "")
                    
                    # 1. 纯净清洗：斩断原网站末尾长长的无用废话后缀
                    clean_title = full_title
                    for word in ["full match replay", "full match", "replay", "highlights"]:
                        if word in clean_title.lower():
                            w_idx = clean_title.lower().find(word)
                            clean_title = clean_title[:w_idx].strip()
                    
                    # 2. 提取原生日期并清洗为“月日”（剥离年份，留作标签展示）
                    display_date = "近期"
                    date_match = re.search(r'(\d{1,2}\s+[a-zA-Z]+)\s+\d{4}', clean_title)
                    if date_match:
                        display_date = date_match.group(1).strip()  # 只要 “日 月”，例如 "25 Oct"
                        full_date_str = re.search(r'(\d{1,2}\s+[a-zA-Z]+\s+\d{4})', clean_title).group(1)
                        clean_title = clean_title.replace(full_date_str, "").strip()
                    
                    # 3. 切分出主队与客队
                    vs_match = re.search(r'\s+[vV][sS]\s+', clean_title)
                    if vs_match:
                        vs_str = vs_match.group(0)
                        parts = clean_title.split(vs_str)
                        home_team = parts[0].strip()
                        away_team = parts[1].strip()
                    else:
                        idx = clean_title.lower().find("vs")
                        home_team = clean_title[:idx].strip()
                        away_team = clean_title[idx+2:].strip()
                    
                    # 清洗可能遗留的包裹中划线
                    home_team = home_team.rstrip('-').strip()
                    away_team = away_team.lstrip('-').strip()
                    
                    # 4. 🚀 调用 7 格宽度分配逻辑加工名字
                    home_final = format_team_name(home_team)
                    away_final = format_team_name(away_team)
                    
                    # 5. 按照最终排版拼装数据
                    tag_remark = display_date                    # 🏷️ 标签角落栏：25 Oct
                    title_name = f"{home_final} - {away_final}"   # 📺 大字标题栏：Man Uni - Chelsea
                    
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