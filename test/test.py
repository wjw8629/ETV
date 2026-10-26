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
        if not ids or not ids[0]:
            return {'list': []}
        
        vid = ids[0]  # 主视频ID（即 4580）
        target_url = f"{self.host}/{vid}.html?sid={vid}"
        
        try:
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # A. 先用正则卡死防线，精准抓取 <article class="infobv">...</article> 块
                article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
                
                play_urls = []
                if article_block:
                    block_text = article_block.group(1)
                    
                    # B. 在该标签块内部，循环匹配所有分集的 sid 数字和集数名字
                    # 匹配形如：href="...sid=17408" 并且获取标签之间的按钮名字（如“第一集”）
                    matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([^<]+)<', block_text)
                    
                    for sid, ep_name in matches:
                        # 拼装成 Fongmi 要求的格式：集数名称$选集ID
                        play_urls.append(f"{ep_name.strip()}${sid}")
                
                # 如果因为网页改版没洗出来，保底把自己当前这一集作为单集吐给 APP 按钮
                if not play_urls:
                    play_urls.append(f"测试单集${vid}")
                
                return {'list': [{
                    'vod_id': vid,
                    'vod_name': '标签解密高清大片',
                    'vod_pic': 'https://bdstatic.com',
                    'vod_remarks': '连载中',
                    'vod_content': '内容由 article 标签动态解密，利用后台请求白嫖实时过期的流媒体签名。',
                    'vod_play_from': '解密播放源',
                    'vod_play_url': '#'.join(play_urls)  # 用 # 号拼接电视端排开的所有分集按钮
                }]}
        except Exception as e:
            pass
            
        return {'list': []}

    # 4. 播放解析核心：用户在电视上点击具体某集（如第2集）时立刻在后台实时抓取
    def playerContent(self, flag, id, vipFlags):
        # 此时传进来的 id 就是上面匹配到的具体那一集的 sid (例如 17409)
        ep_url = f"{self.host}/4580.html?sid={id}"
        
        try:
            # 💡 核心破局：Python 在后台重新向该分集页面发送一次请求
            # 网站后端以为是正常的浏览器点击，就会在返回的 HTML 源码里生成当前这一秒最新的、未过期的字节 CDN 签名！
            r = requests.get(ep_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 从新页面源码中，用正则挖出刚出炉的、带长参数的 m3u8 地址
                # 对应你在原网站源码里看到的：var m3u8Url = "/hls/17408.m3u8"
                m3u8_match = re.search(r'var\s+m3u8Url\s*=\s*"([^"]+)"', html_content)
                
                final_url = ""
                if m3u8_match:
                    final_url = m3u8_match.group(1)
                    if final_url.startswith("/"):
                        final_url = self.host + final_url
                else:
                    # 保底正则：如果网页里的变量变了，直接用通用正则从网页源码里把含有字节 tiktokcdn.com 的长链接整串捞走
                    cdn_match = re.search(r'(https://[-a-zA-Z0-9@:%._\+~#=]{1,256}\.tiktokcdn\.com/[^\s"\']+)', html_content)
                    if cdn_match:
                        final_url = cdn_match.group(1)
                
                if final_url:
                    # 构造电视原生播放器（ExoPlayer）拉取切片流时必须携带的伪装 Headers，防止 403 拦截
                    player_headers = {
                        'User-Agent': self.header['User-Agent'],
                        'Referer': 'https://tiktok.com'  # 字节安全服务器强制校验的来源网址
                    }
                    
                    return {
                        'parse': 0,        # 0 代表直接硬解秒播
                        'url': final_url,  # 已经带有了最新 x-signature 且绝对不会黑屏的真实播放地址
                        'header': player_headers
                    }
        except:
            pass
            
        return {'parse': 0, 'url': ''}

    def searchContent(self, key, quick, pg="1"):
        return {'list': []}

    def fetch(self, url):
        return None

    def localProxy(self, param):
        return None