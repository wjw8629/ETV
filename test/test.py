# -*- coding: utf-8 -*-
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        # 必须返回一个名字
        return 'InfobvSpider'

    def init(self, extend=""):
        # ⚠️ 请把这里换成你那个网站的真实主域名
        self.host = 'https://soccerfull.net'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }

    # 🔥 第一步核心：下发分类标签
    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        
        # 提示改动：主页最新改成了斜杠 '/'
        result['class'].append({'type_name': '最新', 'type_id': '/'})
        result['class'].append({'type_name': '欧冠', 'type_id': '/cate/premier-league'})
        result['class'].append({'type_name': '英超', 'type_id': '/cate/premier-league'})
        result['class'].append({'type_name': '西甲', 'type_id': '/cate/laliga'})
        result['class'].append({'type_name': '德甲', 'type_id': '/cate/bundesliga'})
        result['class'].append({'type_name': '意甲', 'type_id': '/cate/serie-a'})
        result['class'].append({'type_name': '法甲', 'type_id': '/cate/laliga'})
        return result

    # ==========================================
    # 以下全为空壳保底函数，确保 Fongmi 能够编译通过
    # ==========================================
    def homeVideoContent(self):
        return {}

        # 核心：根据点击的标签网址和当前页码（pg），去抓取对应的视频封面墙
    def categoryContent(self, tid, pg, filter, extend):
        # 初始化 Fongmi 标准的列表数据结构
        # pagecount 设为 999 允许电视端无限向下翻页加载
        result = {'list': [], 'page': int(pg), 'pagecount': 999, 'limit': 24, 'total': 0}
        
        # 1. 自动拼接出带页码的分类网页网址
        # 如果是主页(tid为'/')的第一页，目标网址就是 self.host + /?page=1
        # 如果是电影(tid为'/movie.html')的第二页，目标网址就是 self.host + /movie.html?page=2
        connect_char = '&' if '?' in tid else '?'
        target_url = f"{self.host}{tid}{connect_char}page={pg}"
        
        try:
            import requests
            import re
            
            # 2. 发起请求获取当前页面的 HTML 源码
            r = requests.get(target_url, headers=self.header, timeout=10)
            if r.status_code == 200:
                html_content = r.text
                
                # 3. 🔍 升级版通用正则：同时完美兼容 <h2> 和 <h3> 标签
                reg_rule = r'href="/[a-zA-Z0-9-]+-(\d+)\.html"[\s\S]*?src="([^"]+)"[\s\S]*?<(h2|h3)>([^<]+)</\3>'
                matches = re.findall(reg_rule, html_content)
                
                vod_list = []
                for match_item in matches:
                    vid = match_item[0]       # 挖出来的数字 ID (如4659)
                    pic_url = match_item[1]   # 图片路径
                    name = match_item[3]      # 匹配出来的真实标题（在第4个捕获组里）
                    
                    # 自动补全可能存在的相对图片路径
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    # 4. 将清洗好的数据，打包塞入符合 Fongmi 规范的卡片列表里
                    vod_list.append({
                        'vod_id': vid,               
                        'vod_name': name.strip(),     
                        'vod_pic': pic_url,          
                        'vod_remarks': f'ID:{vid}'    
                    })
                
                # 5. 把拼好的封面墙返回
                result['list'] = vod_list
                result['total'] = len(vod_list)
                
        except:
            pass
            
        return result

        # 核心：点击视频海报进入详情页，完美提取出“Full Match in En”和“Full Match”的集数按钮
    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        
        vid = ids[0]  # 拿到上一级传过来的数字 ID（例如 4659）
        target_url = f"{self.host}/{vid}.html"  # 拼接出原网站该视频的完整路由
        
        try:
            import requests
            import re
            
            # 1. 爬取该视频单独的集数页面
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 2. 🔍 正则第一步：缩小防线，精准斩断获取 <article class="infobv"> 的文本块
                article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
                
                play_urls = []
                if article_block:
                    block_text = article_block.group(1)
                    
                    # 3. 🔍 正则第二步：在这个局部的分集块内部，精准捞取所有集数的 sid 数字和显示的按钮文本
                    # 根据你发来的源码特征：匹配 href="...sid=17964" 并且捕获 > 与 < 之间的文本（如 Full Match in En）
                    matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([\s\S]*?)</', block_text)
                    
                    for sid, ep_name in matches:
                        # 4. 打包符合 Fongmi 规范的选集格式：“集数名称$选集独立sid”
                        # 比如在电视上就会显示：[Full Match in En] 和 [Full Match]
                        play_urls.append(f"{ep_name.strip()}${sid}")
                
                # 如果因为特殊原因没洗到任何分集，保底把自己作为单集吐出
                if not play_urls:
                    play_urls.append(f"播放正片${vid}")
                
                # 5. 打包将所有分集数据抛回给电视端
                return {'list': [{
                    'vod_id': vid,
                    'vod_name': '体育高清详情集锦',
                    'vod_play_from': '标签解密视频源',
                    'vod_play_url': '#'.join(play_urls)  # ⚠️ 关键：多个集数按钮之间用 # 号完美隔开
                }]}
        except:
            pass
            
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
