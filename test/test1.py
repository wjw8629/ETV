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
        except:
            pass
        return result

    def searchContent(self, key, quick):
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """
        4. 播放页终极优化：带上专属伪装头，配合 JS 自动点击完成嗅探
        """
        result = {'parse': 1, 'playUrl': '', 'url': id}
        
        # 🔥 根据你抓包获取的 F12 头部，精准复刻防盗链伪装
        result['header'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0',
            'Referer': 'https://playmogo.com/', # 强制锁定为主域名防盗链源头
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US',
            'Connection': 'keep-alive'
        }
        
        # 自动化 JavaScript 点击脚本注入
        result['js'] = """
        (function() {
            var timer = setInterval(function() {
                var btn = document.querySelector('.vjs-big-play-button') || 
                          document.querySelector('[class*="play"]') || 
                          document.querySelector('video') || 
                          document.querySelector('#player') ||
                          document.querySelector('.play-button');
                if (btn) {
                    clearInterval(timer);
                    if (btn.tagName === 'VIDEO') {
                        btn.play();
                    } else {
                        btn.click();
                    }
                }
            }, 500);
            setTimeout(function() { clearInterval(timer); }, 10000);
        })();
        """
        return result
