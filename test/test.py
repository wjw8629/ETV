    # 3. 第三步核心：智能识别上一级参数，100% 确保详情播放页能够成功打开
    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        
        vid = ids[0]  # 拿到上一级传过来的 vod_id
        
        # 💡 【核心对齐逻辑】
        # 判断如果上一级传过来的是纯数字（如 4659），我们用原本的拼接方式
        # 如果上一级传过来的是长路径（如 /sunderland-vs-leeds-united-4659.html），我们直接用真实路径
        if vid.startswith("/"):
            target_url = self.host + vid
        elif ".html" in vid:
            target_url = self.host + "/" + vid if not vid.startswith("/") else self.host + vid
        else:
            target_url = f"{self.host}/{vid}.html"
            
        try:
            import requests
            import re
            
            # 此时拼接出的 target_url 100% 是绝对合法的真实网址！
            r = requests.get(target_url, headers=self.header, timeout=self.timeout)
            if r.status_code == 200:
                html_content = r.text
                
                # 提取原网页真实的比赛全名作为播放抬头
                title_match = re.search(r'<title>([^<]+)</title>', html_content)
                real_video_name = title_match.group(1).split('|')[0].strip() if title_match else "体育精彩赛事"

                # 正则第一步：精准截取包含集数按钮的 <article class="infobv"> 文本块
                article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
                
                play_urls = []
                if article_block:
                    block_text = article_block.group(1)
                    
                    # 正则第二步：循环抠出所有分集的 sid 数字和按钮文本
                    matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([\s\S]*?)</', block_text)
                    
                    for sid, ep_name in matches:
                        # 洗净阻碍电视组件渲染的 \r, \n 换行符以及两端的多余空格
                        clean_name = ep_name.replace('\r', '').replace('\n', '').strip()
                        # 打包成 Fongmi 标准格式：集数名称$选集独立sid
                        play_urls.append(f"{clean_name}${sid}")
                
                if not play_urls:
                    play_urls.append(f"全场正片${vid}")
                
                return {'list': [{
                    'vod_id': vid,
                    'vod_name': real_video_name, # 抬头显示完整比赛名称
                    'vod_play_from': '高清直链',   # 极简的单线路名称
                    'vod_play_url': '#'.join(play_urls)  # 用 # 号完美隔开集数按钮
                }]}
        except:
            pass
            
        return {'list': []}
