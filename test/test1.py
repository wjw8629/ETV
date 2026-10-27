# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'FullShowSpider'

    def init(self, extend=""):
        # ⚠️ 确保主域名完全精准，不要带末尾的斜杠
        self.host = 'https://fullmatchshows.com'  
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
        result['class'].append({'type_name': '法甲', 'type_id': '/leagues/ligue-1'})
        
        home_videos = self.homeVideoContent()
        result['list'] = home_videos.get('list', [])
        return result

    def homeVideoContent(self):
        result = {'list': []}
        try:
            response = requests.get(self.host, headers=self.header, timeout=self.timeout)
            if response.status_code != 200:
                return result
            soup = BeautifulSoup(response.text, 'html.parser')
            result['list'] = self.parseVideoList(soup)
        except Exception as e:
            pass
        return result

    def categoryContent(self, tid, pg, filter, extend):
        """
        1. 分类列表页：当在 Fongmi 点击某个分类或翻页时触发。
        """
        result = {'list': [], 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 999}
        try:
            url = self.host + tid
            if int(pg) > 1:
                if url.endswith('/'):
                    url = f"{url}page/{pg}/"
                else:
                    url = f"{url}/page/{pg}/"

            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code != 200:
                return result
                
            soup = BeautifulSoup(response.text, 'html.parser')
            result['list'] = self.parseVideoList(soup)
        except Exception as e:
            pass
        return result

    def parseVideoList(self, soup):
        """
        公共数据解析方法（严格执行：无VS不抓、含Highlights不抓、主客队名称重置逻辑）
        """
        video_list = []
        matches = soup.find_all('a', class_='entry-image-link')
        
        for match in matches:
            img_tag = match.find('img')
            if not img_tag:
                continue
            
            raw_title = img_tag.get('alt', '').strip()
            href = match.get('href', '')
            pic = img_tag.get('src', '')
            
            if not raw_title or not href:
                continue

            lower_title = raw_title.lower()

            # 🔥 【新要求核心过滤】：只要网站海报标题里包含 highlights，说明它是集锦页，直接不要
            if 'highlight' in lower_title:
                continue

            # 1. 判断是否包含 vs，没有则不抓取
            if 'vs' not in lower_title:
                continue

            # 2. 找到实际的 vs 分隔符并切分出主队和客队
            vs_marker = "vs"
            if "VS" in raw_title:
                vs_marker = "VS"
            elif "Vs" in raw_title:
                vs_marker = "Vs"
            
            parts = raw_title.split(vs_marker)
            home_team = parts[0].strip()   # 主队
            away_part = parts[1].strip()   # 客队及后续部分
            
            # 进一步清洗客队名：剔除常见的杂质后缀
            away_team = away_part
            for keyword in ['Full', 'full', 'Match', 'match', 'Replay', 'replay', '&amp;']:
                if keyword in away_team:
                    away_team = away_team.split(keyword)[0].strip()

            vod_id = href.replace(self.host, '')
            
            # 3. 按要求：图片标签（vod_name）变客队名，备注显示主队名
            video_list.append({
                'vod_id': vod_id,
                'vod_name': f"vs {away_team}",                    # 标题：vs 客队名
                'vod_pic': pic,
                'vod_remarks': home_team                        # 备注：主队名
            })
        return video_list

    def detailContent(self, ids):
        """
        2. 详情页：解析具体的播放按钮和多线路
        """
        result = {'list': []}
        vod_id = ids[0]
        url = self.host + vod_id
        
        try:
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code != 200:
                return result
                
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('h1')
            vod_name = title_tag.text.strip() if title_tag else "赛事回放"
            
            # 抓取带 myButton 类的播放跳转标签
            buttons = soup.find_all('a', class_='myButton')
            play_tracks = {}
            
            for btn in buttons:
                btn_text = btn.text.strip()
                btn_href = btn.get('href', '')
                
                if not btn_href:
                    continue
                    
                # 同时也过滤掉页面内可能混入的、文本带有 highlight 词条的按钮
                if 'highlight' in btn_text.lower():
                    continue
                
                # 按照域名对播放源分类
                track_name = "默认线路"
                for domain in ['playmogo', 'vidaraa', 'vidara', 'vixeo']:
                    if domain in btn_href:
                        track_name = f"源-{domain}"
                        break
                
                if track_name not in play_tracks:
                    play_tracks[track_name] = []
                
                play_tracks[track_name].append(f"{btn_text}${btn_href}")
            
            if play_tracks:
                vod_play_from = "$$".join(play_tracks.keys())
                track_urls = []
                for track in play_tracks.keys():
                    track_urls.append("#".join(play_tracks[track]))
                vod_play_url = "$$".join(track_urls)
            else:
                vod_play_from = "暂无回放"
                vod_play_url = "无可用正片$#"

            vod = {
                'vod_id': vod_id,
                'vod_name': vod_name,
                'vod_pic': '', 
                'type_name': '全场赛事',
                'vod_play_from': vod_play_from,
                'vod_play_url': vod_play_url,
                'vod_content': vod_name
            }
            result['list'].append(vod)
            
        except Exception as e:
            pass
            
        return result

    def searchContent(self, key, quick):
        """
        3. 搜索页
        """
        result = {'list': []}
        return result

    def playerContent(self, flag, id, vipFlags):
        """
        4. 播放页重构：针对类似 mogo 这种必须“点击播放”才会触发真实链接的网盘
        """
        result = {'parse': 0, 'playUrl': '', 'url': ''}
        try:
            # 告诉 Fongmi 这是一个需要动态嗅探的网页链接
            result['parse'] = 1  
            result['url'] = id
            
            # 设置通用的防盗链和浏览器伪装头
            result['header'] = {
                'User-Agent': self.header['User-Agent'],
                'Referer': id
            }

            # 🔥 针对各大网盘的自动化交互核心：
            # 很多视频网盘在初始加载时，网页中心会有一个超大的播放按钮（如 .vjs-big-play-button、#player 或 video 标签本身）
            # 我们通过注入一段轻量级的 JavaScript 脚本，在网页加载完后自动去寻找并“猛击”这个播放按钮，从而在后台逼出含有 token 的真实地址
            if 'playmogo' in id or 'vidara' in id or 'vixeo' in id:
                # 这段 JS 会在 webview 载入后自动执行：尝试寻找各种常见的视频播放器按钮并点击它，或者直接拉起 video 播放
                js_click = """
                (function() {
                    var timer = setInterval(function() {
                        var btn = document.querySelector('.vjs-big-play-button') || 
                                  document.querySelector('[class*="play"]') || 
                                  document.querySelector('video');
                        if (btn) {
                            clearInterval(timer);
                            if (btn.tagName === 'VIDEO') {
                                btn.play();
                            } else {
                                btn.click();
                            }
                        }
                    }, 500);
                    // 10秒后超时自动清除定时器
                    setTimeout(function() { clearInterval(timer); }, 10000);
                })();
                """
                # 将该自动化脚本绑定给 Fongmi 播放引擎（部分高级壳子支持通过脚本或特殊配置进行联动嗅探）
                # 同时为了配合一些壳子，我们在规则中允许捕获媒体资源的特定后缀
                result['js'] = js_click

        except Exception as e:
            pass
            
        return result

