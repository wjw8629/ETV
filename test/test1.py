import re
import requests

# 1. 基础配置
host = 'https://soccerfull.net'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': host
}

# 2. 模拟用户在电视上输入搜索词 "Manchester City" 
user_input_key = "Manchester City"
print(f"📺 电视端输入关键词: '{user_input_key}'")

# 3. 核心清洗：转换空格为短横线
clean_key = user_input_key.strip().lower().replace(' ', '-')
search_url = f"{host}/search/{clean_key}"
print(f"📡 自动拼接出的真实搜索请求网址: {search_url}")

try:
    r = requests.get(search_url, headers=headers, timeout=10)
    print(f"服务器响应状态码: {r.status_code}")
    
    if r.status_code == 200:
        html_content = r.text
        
        # 4. 使用全兼容正则捞取数据
        reg_rule = r'href="([^"]+-[0-9]+\.html)"[\s\S]*?src="([^"]+)"[\s\S]*?<(?:h2|h3)>([^<]+)</(?:h2|h3)>'
        matches = re.findall(reg_rule, html_content)
        print(f"📊 该页面成功用正则匹配到的原始卡片数量: {len(matches)} 个\n")
        
        if matches:
            print("🚀 --- 以下为前 3 个视频卡片执行『主客队故意互换』后的数据包预览 ---")
            for idx, (ep_path, pic_url, full_name) in enumerate(matches[:3]):
                full_title = full_name.strip()
                lower_title = full_title.lower()
                
                # 执行切分
                display_name = full_title
                remarks_text = "搜索结果"
                
                if "vs" in lower_title:
                    idx_vs = lower_title.find("vs")
                    home_team = full_title[:idx_vs].strip().rstrip('-').strip()
                    away_team = full_title[idx_vs+2:].strip().lstrip('-').strip()
                    
                    # 遵循你最满意的故意颠倒样式
                    remarks_text = home_team          # 海报角标显主队
                    display_name = f"vs {away_team}"     # 下方标题显 vs 客队
                
                print(f"\n【卡片 {idx+1}】")
                print(f"  ├─ 原始全名: {full_title}")
                print(f"  ├─ 传输 vod_id (网页路径): {ep_path}")
                print(f"  ├─ 标题栏 vod_name (大字显示): {remarks_text}")
                print(f"  └─ 角标栏 vod_remarks (悬浮高亮): {display_name}")
            print("\n--------------------------------------------------------------")
        else:
            print("❌ 警告：未能在搜索页面匹配到任何视频卡片，请检查网页结构！")
            
except Exception as e:
    print(f"测试发生异常: {e}")
