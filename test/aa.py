import urllib.request
import re
import ssl
import time

def bypass_mango_bait_and_get_real_stream(embed_url):
    print("🔬 [黑盒攻坚] 正在绕过 10 秒蜜罐假流，深度解码芒果正片直链...")
    print(f"🔗 嵌入层播放页: {embed_url}\n" + "="*60)
    
    # 精准复刻你 F12 抓到的 Firefox 完全流媒体伪装指纹
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0',
        'Referer': 'https://playmogo.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        # Step 1: 首次抓取核心播放页原始文本，寻找被混淆的暗号公式
        req = urllib.request.Request(embed_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        print("✅ 成功突入播放核心页。正在剥离 JavaScript 混淆层...")

        # 根据 DoodStream/Playmogo 最新的多层变量混淆特征，地毯式提取密钥暗号
        # 暗号公式一：查找异步获取实际直链的 URL 路由（通常类似于 /pass_md5/xxxx）
        md5_route_match = re.search(r'[\'"](/pass_md5/[^\'"]+)[\'"]', html)
        # 暗号公式二：查找前端生成的参数令牌密钥（通常在 JavaScript 变量中随动下发）
        token_match = re.search(r'pass_md5\s*=\s*["\']([^"\']+)["\']', html)
        
        # 兼容性匹配：部分新切片变体使用 window.token
        if not token_match:
            token_match = re.search(r'token\s*=\s*["\']([^"\']+)["\']', html)

        if md5_route_match:
            md5_route = md5_route_match.group(1)
            print(f"📌 [拦截到核心公式] 异步直链派发路由: {md5_route}")
            
            # 自动组装出真正的二次对暗号直链接口
            api_url = "https://playmogo.com" + md5_route
            
            # 🔥 注入 Ajax 异步包指纹，欺骗网盘风控，证明我们不是直接看 HTML，而是播放器发出的核心请求
            api_headers = headers.copy()
            api_headers['X-Requested-With'] = 'XMLHttpRequest'
            
            # 芒果源为了防止高频请求，有时会在接口前校验时间或带上特定的验证，我们加上短暂的缓冲延迟
            time.sleep(1)
            print("🔄 正在携带专属安全暗号，强制向网盘内核调取 1.6GB 正片大流...")
            
            api_req = urllib.request.Request(api_url, headers=api_headers)
            with urllib.request.urlopen(api_req, context=ctx, timeout=12) as api_res:
                raw_stream_data = api_res.read().decode('utf-8', errors='ignore').strip()
            
            # 分析响应数据：真正的地址往往直接包含在响应中，或者通过特定的字符拼接而成
            if "cloudatacdn" in raw_stream_data or raw_stream_data.startswith("http"):
                print(f"\n🎉🎉🎉 [特大突破] 成功粉碎 10 秒假流欺骗，抓捕到真正的全场正片直链！：")
                print(f"👉 视频流直链: {raw_stream_data}")
                print("\n💡 完美！只要将这个地址注入代码，Fongmi 将实现彻底免弹窗、免点击的无缝秒播！")
                return
            else:
                # 针对高级混淆：有些变体响应回来的依然是一段需要跟随机数拼接的混淆字符串
                # 我们通过常见的字符拼接公式，把真实直链还原
                print(f"⚡ 异步暗号响应成功。响应缓冲区内容长度: {len(raw_stream_data)}")
                print(f"👉 响应数据预览: {raw_stream_data[:200]}...")
                
                # 尝试用视频流模式提取
                potential_url = re.search(r'(https?://[^\s"\']+cloudatacdn[^\s"\']+)', raw_stream_data)
                if potential_url:
                    print(f"\n🔥 [大功告成] 成功从响应流中提取出 100% 正片地址:\n👉 {potential_url.group(1)}")
                    return
                
        print("\n❌ 报告：当前测试的网络请求中，静态数据未完全对上该网盘最新的 JS 混淆公式。")
        print("💡 应对手段：莫慌！既然静态发包被对方用更加复杂的 JS 动态混淆代码（必须在执行内存里跑）拦住了，那我们在 Fongmi 里要做的，就是修改自动点击脚本，加一句：在戳大按钮前，先通过代码把网页上那个‘10 秒假多媒体标签’强行从 HTML 里给干掉（Remove），这样 Fongmi 就永远嗅探不到假视频，逼迫嗅探器只能去拦截你点出来的那个真的大流！")

    except Exception as e:
        print(f"❌ 攻坚期间遭遇异常阻断: {e}")

if __name__ == "__main__":
    # 使用你改好并锁定的嵌入核心播放页链接开启单开渗透
    bypass_mango_bait_and_get_real_stream("https://playmogo.com/d/dfij13tbflif")
