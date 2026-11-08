import sys

sys.dont_write_bytecode = True

import requests
import json
import re
import time
import random
import hashlib
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from requests.exceptions import RequestException

thread_num = 5  # 线程数

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Origin": "https://m.miguvideo.com",
    "Pragma": "no-cache",
    "Referer": "https://m.miguvideo.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Support-Pendant": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
    "appCode": "miguvideo_default_h5",
    "appId": "miguvideo",
    "channel": "H5",
    "sec-ch-ua": "\"Chromium\";v=\"150\", \"Microsoft Edge\";v=\"150\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "terminalId": "h5"
}

LIVE = {
    '热门': 'e7716fea6aa1483c80cfc10b7795fcb8',
    '体育': '7538163cdac044398cb292ecf75db4e0',
    '央视': '1ff892f2b5ab4a79be6e25b69d2f5d05',
    '影视': '10b0d04cb23d4ac5945c4bc77c7ac44e',
    '新闻': 'c584f67ad63f4bc983c31de3a9be977c',
    '综艺': '192a12edfef04b5eb616b878f031f32f',
    '少儿': 'fc2f5b8fd7db43ff88c4243e731ecede',
    '纪实': 'e1165138bdaa44b9a3138d74af6c6673'
}
lives = list(LIVE)

output_path = Path(__file__).resolve().parent / 'cctv.migu.m3u'
appVersion = "2600034600"
All_Live = []
FLAG = 0

# 全局去重缓存与线程锁
url_cache = {}          
cache_lock = threading.Lock()


def format_date_ymd():
    current_date = datetime.now()
    return f"{current_date.year}{current_date.month:02d}{current_date.day:02d}"


def is_target_cctv(name):
    if not isinstance(name, str) or any(keyword in name for keyword in ("欧洲", "美洲")):
        return False
    return re.search(r"CCTV\s*-?\s*(?:1[0-7]|[1-9])\s*\+?(?!\d)", name, re.IGNORECASE) is not None


def md5(text):
    md5_obj = hashlib.md5()
    md5_obj.update(text.encode('utf-8'))
    return md5_obj.hexdigest()


def getSaltAndSign(pid):
    timestamp = str(int(time.time() * 1000))
    random_num = random.randint(0, 999999)
    salt = f"{random_num:06d}25"
    suffix = "2cac4f2c6c3346a5b34e085725ef7e33migu" + salt[:4]
    app_t = timestamp + pid + appVersion[:8]
    sign = md5(md5(app_t) + suffix)
    return {
        "salt": salt,
        "sign": sign,
        "timestamp": timestamp
    }


def get_content(pid):
    _headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "apipost-language": "zh-cn",
        "apipost-machine": "bd2d54b7c2002",
        "apipost-platform": "Win",
        "apipost-terminal": "web",
        "apipost-version": "8.2.7",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="150", "Chromium";v="150", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://workspace.apipost.net/guest/apis",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    if pid == "608831231":
        rateType = "2"
        print(f"[特殊处理] 广东卫视 使用 rateType=2")
    else:
        rateType = "3"

    client_id = md5(str(int(time.time() * 1000)))
    result = getSaltAndSign(pid)
    extra_params_str = "&flvEnable=true&super4k=true"

    URL = (f"https://play.miguvideo.com/playurl/v1/play/playurl?"
           f"sign={result['sign']}&rateType={rateType}&contId={pid}&"
           f"timestamp={result['timestamp']}&salt={result['salt']}{extra_params_str}")

    params_list = URL.split("?")[1].split("&")

    header_parameter = [
        {"description": "", "field_type": "string", "is_checked": 1, "key": "AppVersion",
         "value": "2600034600", "not_None": 1, "schema": {"type": "string"}, "param_id": "3c60653273e0b3"},
        {"description": "", "field_type": "string", "is_checked": 1, "key": "TerminalId",
         "value": "android", "not_None": 1, "schema": {"type": "string"}, "param_id": "3c6075c1f3e0e1"},
        {"description": "", "field_type": "string", "is_checked": 1, "key": "X-UP-CLIENT-CHANNEL-ID",
         "value": "2600034600-99000-201600010010028", "not_None": 1, "schema": {"type": "string"}, "param_id": "3c60858bb3e10c"},
        {"description": "", "field_type": "string", "is_checked": 1, "key": "ClientId",
         "value": client_id, "not_None": 1, "schema": {"type": "string"}, "param_id": "clientid_new"}
    ]

    if pid not in ["641886683", "641886773"]:
        header_parameter.append({
            "description": "", "field_type": "string", "is_checked": 1, "key": "appCode",
            "value": "miguvideo_default_android", "not_None": 1, "schema": {"type": "string"}, "param_id": "appcode_new"
        })

    query_parameter = []
    for idx, p in enumerate(params_list):
        if '=' in p:
            k, v = p.split('=', 1)
            query_parameter.append({
                "param_id": f"qp_{idx}",
                "field_type": "string",
                "is_checked": 1,
                "key": k,
                "not_None": 1,
                "value": v,
                "description": ""
            })

    body = {
        "option": {
            "scene": "http_request",
            "lang": "zh-cn",
            "globals": {},
            "project": {
                "request": {
                    "header": {"parameter": header_parameter},
                    "query": {"parameter": query_parameter},
                    "body": {"parameter": []},
                    "cookie": {"parameter": []},
                    "auth": {"type": "noauth"},
                    "pre_tasks": [],
                    "post_tasks": []
                }
            },
            "env": {
                "env_id": "1",
                "env_name": "默认环境",
                "env_pre_url": "",
                "env_pre_urls": {
                    "1": {"server_id": "1", "name": "默认服务", "sort": 1000, "uri": ""},
                    "default": {"server_id": "1", "name": "默认服务", "sort": 1000, "uri": ""}
                },
                "environment": {}
            },
            "cookies": {"switch": 1, "data": []},
            "system_configs": {
                "send_timeout": 0,
                "auto_redirect": -1,
                "max_redirect_time": 5,
                "auto_gen_mock_url": -1,
                "request_param_auto_json": -1,
                "proxy": {
                    "type": 2,
                    "envfirst": 1,
                    "bypass": [],
                    "protocols": ["http"],
                    "auth": {"authenticate": -1, "host": "", "username": "", "password": ""}
                },
                "ca_cert": {"open": -1, "path": "", "base64": ""},
                "client_cert": {}
            },
            "custom_functions": {},
            "collection": [
                {
                    "target_id": "3c5fd6a9786002",
                    "target_type": "api",
                    "parent_id": "0",
                    "name": "MIGU",
                    "request": {
                        "auth": {"type": "inherit"},
                        "body": {
                            "mode": "None",
                            "parameter": [],
                            "raw": "",
                            "raw_parameter": [],
                            "raw_schema": {"type": "object"},
                            "binary": None
                        },
                        "pre_tasks": [],
                        "post_tasks": [],
                        "header": {"parameter": header_parameter},
                        "query": {"parameter": query_parameter, "query_add_equal": 1},
                        "cookie": {"parameter": [], "cookie_encode": 1},
                        "restful": {"parameter": []},
                        "tabs_default_active_key": "query"
                    },
                    "parents": [],
                    "method": "GET",
                    "protocol": "http/1.1",
                    "url": URL,
                    "pre_url": ""
                }
            ],
            "database_configs": {}
        },
        "test_events": [
            {
                "type": "api",
                "data": {
                    "target_id": "3c5fd6a9786002",
                    "project_id": "57a21612a051000",
                    "parent_id": "0",
                    "target_type": "api"
                }
            }
        ]
    }

    body_str = json.dumps(body, separators=(",", ":"))
    proxy_url = "https://workspace.apipost.net/proxy/v2/http"

    resp = None
    try:
        resp = requests.post(proxy_url, headers=_headers, data=body_str, timeout=15)
        result = resp.json()
        response_body = result["data"]["data"]["response"]["body"]
        return json.loads(response_body)
    except Exception as e:
        print(f"Apipost 返回解析失败: {e}")
        # ✅ 修复点1：安全地打印异常日志，避免 NameError 引起的二次崩溃
        if resp is not None:
            print("原始响应:", resp.text[:500])
        else:
            print("未能成功获取到响应对象（可能由于请求超时或网络中断）。")
        raise


def getddCalcu720p(url, pID):
    puData = url.split("&puData=")[1]
    keys = "cdabyzwxkl"
    ddCalcu = []
    for i in range(0, int(len(puData) / 2)):
        ddCalcu.append(puData[int(len(puData)) - i - 1])
        ddCalcu.append(puData[i])
        if i == 1:
            ddCalcu.append("v")
        if i == 2:
            ddCalcu.append(keys[int(format_date_ymd()[2])])
        if i == 3:
            ddCalcu.append(keys[int(pID[6])])
        if i == 4:
            ddCalcu.append("a")
    return f'{url}&ddCalcu={"".join(ddCalcu)}&sv=10004&ct=android'


def append_All_Live(live, flag, data):
    channel_name = data["name"]
    channel_pid = data["pID"]
    
    # 创建双向锁定组合键 (名字, pid)
    cache_key = (channel_name, channel_pid)
    
    with cache_lock:
        if cache_key in url_cache:
            playurl, rate = url_cache[cache_key]
            content = f'#EXTINF:-1 tvg-id="{channel_name}" tvg-name="{channel_name}" tvg-logo="{data["pics"]["highResolutionH"]}" group-title="{live}",{channel_name}\n{playurl}\n'
            All_Live[flag] = content
            print(f'频道 [{channel_name}] (PID:{channel_pid}) -> [通过Name+PID双重校验] 从去重缓存秒速同步成功')
            return

    max_retries = 3  
    base_delay = 2   

    for attempt in range(1, max_retries + 1):
        try:
            respData = get_content(channel_pid)
            raw_url = respData["body"]["urlInfo"]["url"]
            real_pid = respData.get("body", {}).get("content", {}).get("contId", channel_pid)
            
            playurl = getddCalcu720p(raw_url, real_pid)
            rate = respData["body"]["urlInfo"].get("rateType", "未知")

            with cache_lock:
                url_cache[cache_key] = (playurl, rate)

            content = f'#EXTINF:-1 tvg-id="{channel_name}" tvg-name="{channel_name}" tvg-logo="{data["pics"]["highResolutionH"]}" group-title="{live}",{channel_name}\n{playurl}\n'
            All_Live[flag] = content
            print(f'频道 [{channel_name}] rateType={rate} → 更新成功')
            return

        except (RequestException, KeyError, IndexError, json.JSONDecodeError) as e:
            if attempt < max_retries:
                delay = (base_delay ** attempt) + random.uniform(0.5, 1.5)
                print(f'频道 [{channel_name}] 第 {attempt} 次请求失败 ({e})，将在 {delay:.2f} 秒后重试...')
                time.sleep(delay)
            else:
                print(f'频道 [{channel_name}] 更新失败！已达到最大重试次数。 ERROR: {e}')


def update(live, url):
    global FLAG, All_Live
    pool = ThreadPoolExecutor(thread_num)
    response = requests.get(url, headers=headers).json()
    # 提取初始列表
    rawList = response["body"]["dataList"]
    
    # 只请求需要的 CCTV 频道，避免为无关频道获取播放地址
    dataList = [item for item in rawList if is_target_cctv(item.get("name"))]
    print(f"分类 [{live}]：接口频道 {len(rawList)} 个，匹配 CCTV {len(dataList)} 个")
    
    # ✅ 修复点2：前置一次性扩容占位符，保护 FLAG 在多线程上下文下的定位安全性
    current_start_flag = FLAG
    All_Live.extend([""] * len(dataList))
    FLAG += len(dataList)
    
    for flag_offset, data in enumerate(dataList):
        pool.submit(append_All_Live, live, current_start_flag + flag_offset, data)
        
    pool.shutdown()


def get_channel_name(extinf):
    return extinf.rsplit(',', 1)[-1].strip()


def is_cctv_channel(extinf):
    name = get_channel_name(extinf)
    excluded_names = ("美洲", "欧洲", "CGTN", "老故事", "发现之旅", "中学生")
    if any(keyword in name for keyword in excluded_names):
        return False
    return re.search(r'CCTV\s*-?\s*(?:1[0-7]|[1-9])\s*\+?(?!\d)', name, re.IGNORECASE) is not None


def cctv_sort_key(channel):
    name = get_channel_name(channel[0])
    match = re.search(r'CCTV\s*-?\s*(1[0-7]|[1-9])\s*(\+)?', name, re.IGNORECASE)
    if not match:
        return (99, 0, name.lower())
    return (int(match.group(1)), 1 if match.group(2) else 0, name.lower())


def update_group_title(extinf):
    extinf = re.sub(r'\s*group-title="[^"]*"', '', extinf)
    if ',' in extinf:
        metadata, name = extinf.rsplit(',', 1)
        extinf = f'{metadata.strip()},group-title="CCTV",{name.strip()}'
    return extinf.strip()


def simplify_cctv_name(extinf):
    name = get_channel_name(extinf)
    match = re.search(r'CCTV\s*-?\s*(1[0-7]|[1-9])\s*(\+)?', name, re.IGNORECASE)
    if not match:
        return extinf

    channel_id = f"CCTV{match.group(1)}{'+' if match.group(2) else ''}"
    extinf = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{channel_id}"', extinf)
    extinf = re.sub(r'tvg-name="[^"]*"', f'tvg-name="{channel_id}"', extinf)
    metadata, _ = extinf.rsplit(',', 1)
    return f'{metadata},{channel_id}'


def build_cctv_playlist(channel_contents):
    channels = []
    seen = set()
    for content in channel_contents:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(lines) < 2 or not lines[0].startswith('#EXTINF:'):
            continue

        extinf, url = lines[0], lines[-1]
        if not is_cctv_channel(extinf):
            continue

        tvg_id = re.search(r'tvg-id="([^"]+)"', extinf)
        tvg_name = re.search(r'tvg-name="([^"]+)"', extinf)
        key = (tvg_id.group(1) if tvg_id else "") or (tvg_name.group(1) if tvg_name else "") or extinf
        if key in seen:
            continue
        seen.add(key)
        channels.append((extinf, url))

    channels.sort(key=cctv_sort_key)
    output_lines = ["#EXTM3U", "", "# ================================== 央视 CCTV 频道 ==================================", ""]
    for extinf, url in channels:
        output_lines.extend((simplify_cctv_name(update_group_title(extinf)), url, ""))

    print(f"最终 CCTV 频道数：{len(channels)}")
    return "\n".join(output_lines)


def main():
    global All_Live, FLAG
    All_Live = []
    FLAG = 0
    with cache_lock:
        url_cache.clear()
    
    for live in lives:
        print(f"\n分类 ----- [{live}] ----- 开始更新...")
        url = f'https://program-sc.miguvideo.com/live/v2/tv-data/{LIVE[live]}'
        update(live, url)
    
    playlist = build_cctv_playlist(content for content in All_Live if content)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(playlist)
    print("\n全部更新完成！M3U 文件已生成：", output_path)


if __name__ == "__main__":
    main()
