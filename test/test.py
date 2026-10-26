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
