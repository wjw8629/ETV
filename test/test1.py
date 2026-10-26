import requests
import re

# ⚠️ 换成你刚才测试成功的那个真实分类网址
target_url = "https://soccerfull.net/cate/premier-league" 

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    r = requests.get(target_url, headers=headers, timeout=10)
    if r.status_code == 200:
        html = r.text
        
        # 🔍 诊断核心：找出所有包含 .html 且里面带有 class 或图片的关键区域
        # 帮我们把第一个视频卡片的完整 HTML 块切出来
        blocks = re.findall(r'<a href="[^"]+-[0-9]+\.html"[\s\S]*?</a>', html)
        
        if blocks:
            print("\n🚨 【抓包成功】以下是该页面第一个视频卡片的真实 HTML 结构：\n")
            print(blocks[0])
            print("\n======================================================\n")
        else:
            # 如果切不到，说明可能连 href 格式都和主页微调了，打印前 5 个包含 .html 的原始标签
            lines = html.split('\n')
            matched_lines = [line.strip() for line in lines if '.html' in line and 'img' in line][:3]
            print("\n🚨 【备用抓包】未切到完整块，提取到包含图片和链接的原始行：\n")
            for idx, line in enumerate(matched_lines):
                print(f"行 {idx+1}: {line}")
except Exception as e:
    print(f"排查出错: {e}")
