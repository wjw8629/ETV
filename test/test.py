# -*- coding: utf-8 -*-
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        # 必须返回一个名字
        return 'InfobvSpider'

    def init(self, extend=""):
        # ⚠️ 请把这里换成你那个网站的真实主域名
        self.host = 'https://你的视频网站域名.com'  
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

    def categoryContent(self, tid, pg, filter, extend):
        return {'list': [], 'page': int(pg), 'pagecount': 0, 'limit': 24, 'total': 0}

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
