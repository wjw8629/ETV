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
        """
        详情页解析：全面启动 playmogo 独占锁定策略
        """
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
                play_urls = []
                
                for btn in buttons:
                    btn_text = btn.text.strip()
                    btn_href = btn.get('href', '')
                    
                    if not btn_href or 'highlight' in btn_text.lower():
                        continue
                    
                    # 🔥【精简核心】：只留下带有 playmogo 的链接，其他任何网盘链接全部抛弃
                    if 'playmogo.com' not in btn_href:
                        continue
                    
                    # 强行加上防弹窗嗅探前缀
                    play_urls.append(f"{btn_text}$fongmi_sniff_{btn_href}")
                
                if play_urls:
                    vod_play_from = "优质芒果源"
                    vod_play_url = "#".join(play_urls)
                else:
                    vod_play_from = "暂无芒果回放"
                    vod_play_url = "无正片可用$#"

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
        4. 播放页终极攻坚：劫持屏蔽所有穿透广告弹窗，纯净自动化点击嗅探
        """
        real_url = id.replace("proxy://", "").replace("fongmi_sniff_", "")
        result = {'parse': 1, 'playUrl': '', 'url': real_url}
        
        # 100% 锁死精准防盗链报头
        result['header'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0',
            'Referer': 'https://playmogo.com',
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US',
            'Connection': 'keep-alive'
        }
        
        # 🔥【史诗级防广告注入脚本】：先下毒废掉所有弹窗，再静默点击起播
        result['js'] = """
        (function() {
            // ⭐ 第一步：死死锁住全局弹窗 API，使其完全废掉，从根本上解决“弹出超级多广告网页”的痛点
            window.open = function() { return null; };
            window.openWindow = function() { return null; };
            
            // ⭐ 第二步：全面清洗并拦截网页里的恶意超链接外跳转行为
            var cleanAds = function() {
                var links = document.querySelectorAll('a');
                for (var i = 0; i < links.length; i++) {
                    var link = links[i];
                    // 只要点击可能触发新窗口跳转的，一律废除 href 或限制在原地
                    if (link.getAttribute('target') === '_blank' || link.outerHTML.indexOf('onclick') !== -1) {
                        link.setAttribute('target', '_self');
                        if (link.href && link.href.indexOf('playmogo') === -1 && link.href.indexOf('javascript') === -1) {
                            link.href = 'javascript:void(0);';
                        }
                    }
                }
            };
            
            // 每 200 毫秒疯狂扫描一次页面，动态消灭新长出来的广告超链接
            setInterval(cleanAds, 200);

            # ⭐ 第三步：在完全安全无弹窗的环境中，高频寻找真正的播放大按钮并安全戳活
            var timer = setInterval(function() {
                var btn = document.querySelector('.vjs-big-play-button') || 
                          document.querySelector('#os_player') || 
                          document.querySelector('video') || 
                          document.getElementById('player') ||
                          document.querySelector('.play-button') ||
                          document.getElementById('vplayer');
                if (btn) {
                    clearInterval(timer);
                    if (btn.tagName === 'VIDEO') {
                        btn.play();
                    } else {
                        // 触发点击，此时 window.open 已被废，所有弹窗广告全部哑火！
                        btn.click();
                    }
                }
            }, 300);
            
            setTimeout(function() { clearInterval(timer); }, 12000);
        })();
        """
        return result
