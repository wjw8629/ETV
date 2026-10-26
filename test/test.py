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

            # 3. 第三步核心：用户在电视上点击海报封面进入详情页，通过绝对路径，完美提取出集数按钮
    def detailContent(self, ids):
        if not ids or not ids:
            return {'list': []}
        
        vid = ids  # 拿到上一级传过来的完整网页路径（例如 /sunderland-vs-leeds-united-4659.html）
        target_url = self.host + vid  # 拼接出该场比赛网页的真实网址
        
        try:
            import requests
            import re
            
            # 请求该比赛播放页的源码
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # A. 体验优化：直接用正则把网页里的真实比赛全名捞出来，作为详情页和播放器上方的真实抬头！
                title_match = re.search(r'<title>([^<]+)</title>', html_content)
                real_video_name = title_match.group(1).split('|')[0].strip() if title_match else "体育精彩赛事"

                # B. 正则第一步：精准截取 <article class="infobv"> 的局部文本块
                article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
                
                play_urls = []
                if article_block:
                    block_text = article_block.group(1)
                    
                    # C. 正则第二步：在分集块内部，精准捞取所有选集的 sid 数字和按钮文本
                    matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([\s\S]*?)</', block_text)
                    
                    for sid, ep_name in matches:
                        # 💡 强效清洗：彻底剔除掉阻碍电视组件渲染的 \r, \n 换行符以及两端多余空格
                        clean_name = ep_name.replace('\r', '').replace('\n', '').strip()
                        # 打包成 Fongmi 标准集数格式：“集数名称$选集独立sid”
                        play_urls.append(f"{clean_name}${sid}")
                
                if not play_urls:
                    # 保底处理
                    play_urls.append(f"全场正片${vid}")
                
                # 返回符合 Fongmi 详情页标准的规范字典
                return {'list': [{
                    'vod_id': vid,
                    'vod_name': real_video_name, # 抬头显示完整比赛名称
                    'vod_pic': f"{self.host}/imgs/{vid.split('-')[-1].replace('.html', '')}.png", # 自动还原图片
                    'vod_play_from': '极速直链',    # 干净的单线路名称，去掉多余的 flag 干扰
                    'vod_play_url': '#'.join(play_urls)  # 用 # 号完美隔开集数按钮
                }]}
        except:
            pass
            
        return {'list': []}


    # 4. 第四步：大结局播放解析！当用户在电视端点击具体某个集数按钮时触发
    def playerContent(self, flag, id, vipFlags):
        # 此时传进来的 id 就是我们在详情页打包给按钮的独立 sid 数字（例如 17964）
        
        # 💡 顺藤摸瓜终点：直接替换并拼接出原网站存放于本地的公共 M3U8 直链地址！
        real_m3u8_url = f"{self.host}/hls/{id}.m3u8"
        
        # 构造电视原生播放器（ExoPlayer / IJKPlayer）拉取切片流时必须携带的伪装 Headers，强破字节 CDN 的 403 拦截
        player_headers = {
            'User-Agent': self.header['User-Agent'],
            'Referer': 'https://tiktok.com'  # 字节安全加速服务器强制校验的宿主域名
        }
        
        # 完美交付
        return {
            'parse': 0,        # 0 代表让电视端直接进行原生内核硬解，不走任何多余嗅探，速度拉满
            'url': real_m3u8_url,
            'header': player_headers
        }


    def searchContent(self, key, quick, pg="1"):
        return {'list': []}

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass
