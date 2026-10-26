# -*- coding: utf-8 -*-
import requests
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return '标签网址测试源'

    def init(self, extend=""):
        # ⚠️ 请把这里换成你那个网站的真实主域名
        self.host = 'https://soccerfull.net'  
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    # 🔥 第一步：将各个标签名和它们各自的“单独网址路径”绑定
    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        
        # 💡 核心改动：把 type_id 直接赋值为该分类的单独网页路径（或完整网址）
        # ⚠️ 请根据你在原网站上看到的实际网址，把后面的路径（如 /movie/）修改精准
        result['class'].append({'type_name': '最新', 'type_id': '/'})
        result['class'].append({'type_name': '欧冠', 'type_id': '/cate/premier-league'})
        result['class'].append({'type_name': '英超', 'type_id': '/cate/premier-league'})
        result['class'].append({'type_name': '西甲', 'type_id': '/cate/laliga'})
        result['class'].append({'type_name': '德甲', 'type_id': '/cate/bundesliga'})
        result['class'].append({'type_name': '意甲', 'type_id': '/cate/serie-a'})
        result['class'].append({'type_name': '法甲', 'type_id': '/cate/laliga'})
        
         # 核心：根据点击的标签网址（tid），去抓取对应的视频封面墙
    def categoryContent(self, tid, pg, filter, extend):
        # 1. 初始化 Fongmi 标准的列表数据结构
        result = {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 24, 'total': 0}
        
        # 2. 自动拼接出当前标签的完整网页网址
        # 如果点“最新内容”，tid 是 '/'，拼接出来就是：https://xn--eqrt2g.com
        # 如果点“电影频道”，tid 是 '/movie.html'，拼接出来就是：https://xn--eqrt2g.commovie.html
        target_url = self.host + tid
        
        try:
            # 3. 在后台偷偷请求这个网页的源码
            import requests
            import re
            r = requests.get(target_url, headers=self.header, timeout=10)
            if r.status_code == 200:
                html_content = r.text
                
                # 4. 🔍 核心提取：用正则表达式从网页源码中把所有视频的 sid、图片、名字抠出来
                # ⚠️ 请注意：这里的正则格式需要根据你网页主页的实际排版进行调校
                matches = re.findall(r'href="[^"]*sid=(\d+)"[\s\S]*?src="([^"]+)"[\s\S]*?<span>([^<]+)</span>', html_content)
                
                vod_list = []
                for sid, pic_url, name in matches:
                    # 自动补全可能存在的相对图片路径
                    if pic_url.startswith("/"):
                        pic_url = self.host + pic_url
                        
                    # 5. 将清洗好的数据，打包塞入符合 Fongmi 规范的卡片字典里
                    vod_list.append({
                        'vod_id': sid,               # 传给下一步详情页的独立选集/专辑数字
                        'vod_name': name.strip(),     # 电视封面上显示的视频标题
                        'vod_pic': pic_url,          # 封面图片直链
                        'vod_remarks': '点播'         # 卡片右下角的备注文本
                    })
                
                # 6. 把拼好的封面墙塞回结果里
                result['list'] = vod_list
                result['total'] = len(vod_list)
                
        except:
            pass
            
        return result
