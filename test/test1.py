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
        vod_id = ids
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
                    
                    # 严格限定芒果单源锁定策略
                    if 'playmogo.com' not in btn_href:
                        continue
                    
                    # 强制在前置阶段将外壳 /d/ 直接转换为嵌入播放页 /e/ 格式，直接剥离弹窗保护层
                    embed_href = btn_href.replace('/d/', '/e/')
                    
                    # 使用 proxy:// 强行拦截随动弹窗，牢牢锁在软件内层嗅探
                    play_urls.append(f"{btn_text}$proxy://{embed_href}")
                
                if play_urls:
                    vod_play_from = "精选芒果正片源"
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
        播放页终极重构：消灭 10 秒诱饵假流，物理粉碎弹窗，诱导抓捕真实大流轨
        """
        real_url = id.replace("proxy://", "")
        result = {'parse': 1, 'playUrl': '', 'url': real_url}
        
        # 精准注入你抓包成功的 Firefox 158 视频播放指纹头
        result['header'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0',
            'Referer': 'https://playmogo.com',  # 锁死绝对宿主 Referer，防止因页面差异触发网盘风控
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US',
            'Connection': 'keep-alive'
        }
        
        # 🚀【战术级脚本注入】：开局蒸发蜜罐、完全按死弹窗、高频戳爆正片
        result['js'] = """
        (function() {
            // ⭐ 核心绝招一：开局立刻把网页里默认存在、用来欺骗 Fongmi 提前收网的 10 秒假多媒体标签强行拔掉！
            // 这能让软件的嗅探器一时间在网页里抓不到任何假流，被迫老老实实守在原地等待！
            var meltBait = function() {
                var baitVideo = document.querySelector('video');
                if (baitVideo) {
                    baitVideo.removeAttribute('src');
                    baitVideo.load();
                    baitVideo.parentNode && baitVideo.parentNode.removeChild(baitVideo);
                }
            };
            // 连切两次，确保假多媒体轨道从 HTML 里完全物理蒸发
            meltBait();
            setTimeout(meltBait, 150);

            // ⭐ 核心绝招二：把 window.open 强行改写成废函数，彻底解决“弹出超级多垃圾网页”的痛点
            window.open = function() { return null; };
            window.openWindow = function() { return null; };
            
            // 地毯式清洗穿透广告超链接，限制其原地打转，防止其偷偷触发任何间接弹窗
            var sterilizeAds = function() {
                var tags = document.querySelectorAll('a');
                for (var i = 0; i < tags.length; i++) {
                    var a = tags[i];
                    if (a.getAttribute('target') === '_blank' || a.outerHTML.indexOf('onclick') !== -1) {
                        a.setAttribute('target', '_self');
                        if (a.href && a.href.indexOf('playmogo') === -1 && a.href.indexOf('javascript') === -1) {
                            a.href = 'javascript:void(0);';
                        }
                    }
                }
            };
            setInterval(sterilizeAds, 200);

            // ⭐ 核心绝招三：在干净无诱饵、无弹窗的高安全环境下，高频去触发点击真正的播放器核心触点
            var clickCount = 0;
            var snifferTimer = setInterval(function() {
                var targetBtn = document.querySelector('.vjs-big-play-button') || 
                                document.querySelector('#os_player') || 
                                document.getElementById('player') ||
                                document.querySelector('.play-button') ||
                                document.getElementById('vplayer');
                if (targetBtn) {
                    // 如果它在点击后又偷偷生出了新的 video 标签，说明真正的异步 cloudatacdn 流被我们点出来了！
                    if (targetBtn.tagName === 'VIDEO') {
                        targetBtn.play();
                    } else {
                        targetBtn.click();
                    }
                    clickCount++;
                    // 连戳 3 次彻底戳活隐藏的前端异步网络请求后，清除自身定时器
                    if (clickCount >= 3) {
                        clearInterval(snifferTimer);
                    }
                }
            }, 300);
            
            setTimeout(function() { clearInterval(snifferTimer); }, 10000);
        })();
        """
        return result
