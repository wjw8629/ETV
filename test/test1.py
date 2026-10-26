import requests
import re

# ⚠️ 1. 请把这里换成你那个网站的真实主域名
host = 'https://soccerfull.net'  

# ⚠️ 2. 请把这里换成任意一个你在第二步里能成功显示封面墙的真实视频路径
# 比如以你发给我的那个西甲/英超比赛网页路径为例
test_vid_path = '/sunderland-vs-leeds-united-4659.html'  

target_url = host + test_vid_path
print(f"正在模拟请求详情页网址: {target_url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': host
}

try:
    r = requests.get(target_url, headers=headers, timeout=10)
    print(f"服务器返回状态码: {r.status_code}")
    
    if r.status_code == 200:
        html_content = r.text
        
        # 🔍 诊断第一步：尝试卡死并提取 <article class="infobv"> 块
        article_block = re.search(r'<article[^>]*class="infobv"[^>]*>([\s\S]*?)</article>', html_content)
        
        if article_block:
            block_text = article_block.group(1)
            print("\n🚨 【抓包成功】成功定位到了 <article class=\"infobv\"> 标签块！")
            print("--- 标签块内部原始 HTML 预览 ---")
            print(block_text.strip())
            print("---------------------------------\n")
            
            # 🔍 诊断第二步：尝试用我们的二级正则去提取里面的 sid 和名字
            matches = re.findall(r'href="[^"]*sid=(\d+)"[^>]*>([\s\S]*?)</', block_text)
            print(f"💡 利用二级正则成功提取出的分集数据对列表: {matches}")
            
        else:
            print("\n❌ 【抓包失败】未能在网页源码中找到 <article class=\"infobv\"> 标签块！")
            print("为了排查原因，以下是网页中前 3 个含有 'sid=' 的原始代码行列表：")
            lines = html_content.split('\n')
            matched_lines = [line.strip() for line in lines if 'sid=' in line][:3]
            for idx, line in enumerate(matched_lines):
                print(f"行 {idx+1}: {line}")
                
except Exception as e:
    print(f"请求测试发生异常: {e}")
