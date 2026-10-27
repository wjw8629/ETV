# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return 'FullShowSpider'

    def init(self, extend=""):
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
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                result['list'] = self.parseVideoList(soup)
        except:
            pass
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': [], 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 999}
        try:
            url = self.host + tid
            if int(pg) > 1:
                url = f"{url.rstrip('/')}/page/{pg}/"
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                result['list'] = self.parseVideoList(soup)
        except:
            pass
        return result

    def parseVideoList(self, soup):
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
            if 'highlight' in lower_title or 'vs' not in lower_title:
                continue

            vs_marker = "vs"
            if "VS" in raw_title:
                vs_marker = "VS"
            elif "Vs" in raw_title:
                vs_marker = "Vs"
            
            parts = raw_title.split(vs_marker)
            home_team = parts[0].strip()   
            away_part = parts[1].strip()   
            
            away_team = away_part
            for keyword in ['Full', 'full', 'Match', 'match', 'Replay', 'replay', '&amp;']:
                if keyword in away_team:
                    away_team = away_team.split(keyword)[0].strip()

            vod_id = href.replace(self.host, '')
            video_list.append({
                'vod_id': vod_id,
                'vod_name': f"vs {away_team}",                    
                'vod_pic': pic,
                'vod_remarks': home_team                        
            })
        return video_list

    def detailContent(self, ids):
        result = {'list': []}
        vod_id = ids[0]
        url = self.host + vod_id
        try:
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('h1')
                vod_name = title_tag.text.strip() if title_tag else "赛事回放"
                
                buttons = soup.find_all('a', class_='myButton')
                play_tracks = {}
                for btn in buttons:
                    btn_text = btn.text.strip()
                    btn_href = btn.get('href', '')
                    if not btn_href or 'highlight' in btn_text.lower():
                        continue
                    
                    track_name = "默认线路"
                    for domain in ['playmogo', 'vidaraa', 'vidara', 'vixeo']:
                        if domain in btn_href:
                            track_name = f"源-{domain}"
                            break
                    
                    if track_name not in play_tracks:
                        play_tracks[track_name] = []
                    
                    # 🔥 拦截改动：将真实的网页地址绑定在自定义标识符后面，拦截 Fongmi 的直接弹窗行为
                    play_tracks[track_name].append(f"{btn_text}$fongmi_sniff_{btn_href}")
                
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
        except:
            pass
        return result

    def searchContent(self, key, quick):
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        # 1. 还原之前详情页传过来的真实独立网盘网页 URL
        real_url = id.replace("fongmi_sniff_", "")
        
        # 2. 精准针对 DoodStream 这类嵌套 iframe 的网盘进行提取升级
        if "dood" in real_url or "doodstream" in real_url:
            try:
                # 在后台悄悄拉取外壳网页
                res = requests.get(real_url, headers=self.header, timeout=self.timeout)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # 强行挖出真正包含视频器的 /e/xxxx 链接
                    iframe = soup.find('iframe')
                    if iframe and iframe.get('src'):
                        iframe_src = iframe.get('src')
                        # 组装成真正的底层播放页：https://doodstream.com
                        if iframe_src.startswith('/'):
                            from urllib.parse import urlparse
                            parsed_uri = urlparse(real_url)
                            domain = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
                            real_url = domain + iframe_src
                        else:
                            real_url = iframe_src
            except:
                pass

        # 3. 拦截弹窗，强制锁在 Fongmi 播放内核中进行强力嗅探
        result = {'parse': 1, 'playUrl': '', 'url': real_url}
        
        # 4. 根据新源码特征，强力注入专属防盗链 Cookie 与伪装头
        result['header'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0',
            'Referer': 'https://playmogo.com',
            'Cookie': 'dref_url=https://fullmatchshows.com/', # 🔥 破解 Doodstream 拦截的核心 Cookie
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US'
        }
        
        # 5. 注入盲点自动脚本：进入真正的 /e/ 播放层后，以 0.3 秒的高频猛击网页上的各种视频触点
        result['js'] = """
        (function() {
            var timer = setInterval(function() {
                var btn = document.querySelector('.vjs-big-play-button') || 
                          document.querySelector('#os_player') || 
                          document.querySelector('video') || 
                          document.getElementById('vplayer') ||
                          document.querySelector('[class*="play"]');
                if (btn) {
                    clearInterval(timer);
                    if (btn.tagName === 'VIDEO') {
                        btn.play();
                    } else {
                        btn.click();
                    }
                }
            }, 300);
            setTimeout(function() { clearInterval(timer); }, 12000);
        })();
        """
        return result
