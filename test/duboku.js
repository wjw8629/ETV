/**
 * 独播库(Duboku) 电脑桌面端 OKPlayer/FongMi 专用纯 JS 爬虫脚本
 * 完美移植自原安卓 Java 类：com.github.catvod.spider.Duboku
 */

// ==================== 【第一部分】全套桌面端环境兼容垫片 (Polyfill) ====================

// 1. 确保全局环境拥有标准 Base64 编码 btoa 方法
if (typeof btoa === 'undefined') {
    globalThis.btoa = function (str) {
        try {
            return Buffer.from(str, 'binary').toString('base64');
        } catch (e) {
            // 如果连 Buffer 都没有，使用纯 JS 兜底实现
            var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
            var output = '';
            for (var block, charCode, idx = 0, map = chars; str.charAt(idx | 0) || (map = '=', idx % 1); output += map.charAt(63 & block >> 8 - idx % 1 * 8)) {
                charCode = str.charCodeAt(idx += 3 / 4);
                if (charCode > 0xFF) {
                    throw new Error("'btoa' failed: The string to be encoded contains characters outside of the Latin1 range.");
                }
                block = block << 8 | charCode;
            }
            return output;
        }
    };
}

// 2. 确保全局环境拥有标准 Base64 解码 atob 方法
if (typeof atob === 'undefined') {
    globalThis.atob = function (str) {
        try {
            return Buffer.from(str, 'base64').toString('binary');
        } catch (e) {
            // 纯 JS 兜底解码逻辑
            var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
            var strStr = String(str).replace(/[=]+$/, '');
            if (strStr.length % 4 == 1) {
                throw new Error("'atob' failed: The string to be decoded is not correctly encoded.");
            }
            for (var bc = 0, bs, fn, idx = 0, output = ''; fn = strStr.charAt(idx++); ~fn && (bs = bc % 4 ? bs * 64 + fn : fn, bc++ % 4) ? output += String.fromCharCode(255 & bs >> (-2 * bc & 6)) : 0) {
                fn = chars.indexOf(fn);
            }
            return output;
        }
    };
}

// ==================== 【第二部分】影视源核心业务逻辑 (Drpy 架构) ====================

var rule = {
    title: '独播库[纯JS电脑优化版]',
    host: 'https://dbokutv.com',
    url: '/vodshow/fyclass-fyarea-fyby-fyclass-fylang----fypage---fyyear',
    searchUrl: '/vodsearch?wd=**',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'Referer': 'https://duboku.tv',
        'Connection': 'keep-alive'
    },
    timeout: 5000,
    
    // 从 Java 源码中的静态标签数据提取出的分类映射
    class_name: '电影#电视剧#综艺#动漫#短剧#港剧#陆剧#日韩剧#台泰剧',
    class_url: '1#2#3#4#21#20#13#15#14',

    // 独播库核心算法包（完美复刻 Java 源码中的签名计算和字符串解密机制）
    DubokuCrypto: {
        // 对应原 Java 中的 a(int i, long j, int i2) 混淆随机数生成器
        generateRandomString: function (len, type) {
            var stringTable = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
            if (type === 88) {
                stringTable = "XYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW";
            }
            var result = '';
            for (var i = 0; i < len; i++) {
                result += stringTable.charAt(Math.floor(Math.random() * stringTable.length));
            }
            return result;
        },

        // 对应原 Java 中的 b() 函数，用于给所有 API 生成带时间戳的数字签名令牌
        getApiSignParams: function () {
            var timestampSeconds = Math.floor(Date.now() / 1000);
            var iNextInt = Math.floor(Math.random() * 800000000) % 800000001;
            var strValueOf = Date.now().toString();
            var mixedStr = (100000000 + iNextInt) + '' + (900000000 - iNextInt);
            
            var sb = '';
            var minLength = Math.min(mixedStr.length, strValueOf.length);
            for (var i = 0; i < minLength; i++) {
                sb += mixedStr.charAt(i);
                sb += strValueOf.charAt(i);
            }
            if (mixedStr.length > minLength) {
                sb += mixedStr.substring(minLength);
            }
            if (strValueOf.length > minLength) {
                sb += strValueOf.substring(minLength);
            }

            var base64Encoded = btoa(sb).replace(/=/g, '.');
            var strA = this.generateRandomString(60, 33);
            var strA2 = this.generateRandomString(38, 88);

            return "?sign=" + strA + "&ssid=" + base64Encoded + "&token=" + strA2;
        },

        // 对应原 Java 中的 d(String str) 解密函数。先按每 10 位步长分段反转，再通过自定义 Base64 还原
        decryptDataField: function (str) {
            if (!str) return '';
            var sb = '';
            var length = str.length;
            var i = 0;
            while (i < length) {
                var chunkSize = Math.min(10, length - i);
                var chunk = str.substring(i, i + chunkSize);
                sb += chunk.split('').reverse().join('');
                i += 10;
            }
            var standardBase64 = sb.replace(/\./g, '=');
            return atob(standardBase64);
        }
    },

    // 1. 首页推荐（由播放器外壳初次加载时自动调用）
    home: function () {
        var sign = this.DubokuCrypto.getApiSignParams();
        var html = request(this.host + '/home' + sign);
        var videos = [];
        try {
            var json = JSON.parse(html);
            json.forEach(function (block) {
                if (block.VodList) {
                    block.VodList.forEach(function (v) {
                        videos.push({
                            vod_id: rule.DubokuCrypto.decryptDataField(v.DId),
                            vod_name: v.Name,
                            vod_pic: rule.DubokuCrypto.decryptDataField(v.TnId),
                            vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                        });
                    });
                }
            });
        } catch (e) {
            print("首页数据解析失败: " + e.message);
        }
        return JSON.stringify({ list: videos });
    },

    // 2. 分类库内容加载（对应你之前报错的“片库内容暂时无法加载”区域）
    category: function (tid, pg, filter, extend) {
        var sign = this.DubokuCrypto.getApiSignParams();
        
        // 解析可能存在的筛选参数
        var area = (extend && extend.area) ? extend.area : '';
        var year = (extend && extend.year) ? extend.year : '';
        var by = (extend && extend.by) ? extend.by : '';
        var clazz = (extend && extend.class) ? extend.class : '';
        var lang = (extend && extend.lang) ? extend.lang : '';

        // 完美对齐 Java 类中的：/vodshow/cateId-area-by-class-lang----page---year
        var path = "/vodshow/" + tid + "-" + area + "-" + by + "-" + clazz + "-" + lang + "----" + pg + "---" + year;
        var requestUrl = this.host + path + sign;
        
        var html = request(requestUrl);
        var videos = [];
        try {
            var json = JSON.parse(html);
            if (json && json.VodList) {
                json.VodList.forEach(function (v) {
                    videos.push({
                        vod_id: rule.DubokuCrypto.decryptDataField(v.DId),
                        vod_name: v.Name,
                        vod_pic: rule.DubokuCrypto.decryptDataField(v.TnId),
                        vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                    });
                });
            }
        } catch (e) {
            print("分类片库解析失败: " + e.message);
        }
        
        return JSON.stringify({
            page: pg,
            pagecount: 999,
            limit: 48,
            total: 9999,
            list: videos
        });
    },

    // 3. 详情页加载（解析具体某部影视剧的简介与剧集列表）
    detail: function (id) {
        var sign = this.DubokuCrypto.getApiSignParams();
        // 此时的 id 本身就是接口所需要的相对路径
        var html = request(this.host + id + sign);
        var vod = {};
        try {
            var json = JSON.parse(html);
            var playList = [];
            if (json.Playlist) {
                json.Playlist.forEach(function (ep) {
                    var epName = ep.EpisodeName;
                    var encryptedVId = ep.VId;
                    var decryptedVId = rule.DubokuCrypto.decryptDataField(encryptedVId);
                    // 按照标准规范组合：剧集名字$解密后的媒体流ID
                    playList.push(epName + "$" + decryptedVId);
                });
            }

            vod = {
                vod_id: id,
                vod_name: json.Name,
                vod_pic: this.DubokuCrypto.decryptDataField(json.TnId),
                vod_year: json.ReleaseYear,
                vod_content: json.Description,
                vod_actor: json.Actor ? json.Actor.join(', ') : '',
                vod_director: json.Director,
                vod_play_from: '独播库快播源',
                vod_play_url: playList.join('#')
            };
        } catch (e) {
            print("详情页解析失败: " + e.message);
        }
        return JSON.stringify({ list: [vod] });
    },

    // 4. 全局搜索
    search: function (wd, quick) {
        var sign = this.DubokuCrypto.getApiSignParams();
        var requestUrl = this.host + '/vodsearch' + sign + '&wd=' + encodeURIComponent(wd);
        var html = request(requestUrl);
        var videos = [];
        try {
            var json = JSON.parse(html);
            if (Array.isArray(json)) {
                json.forEach(function (v) {
                    videos.push({
                        vod_id: rule.DubokuCrypto.decryptDataField(v.DId),
                        vod_name: v.Name,
                        vod_pic: rule.DubokuCrypto.decryptDataField(v.TnId),
                        vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                    });
                });
            }
        } catch (e) {
            print("搜索解析失败: " + e.message);
        }
        return JSON.stringify({ list: videos });
    },

    // 5. 播放内容解析提取（直接解密拿到高清直链，拒绝卡顿）
    play: function (flag, id, flags) {
        var sign = this.DubokuCrypto.getApiSignParams();
        // 原 Java 代码中通过请求具体的视频 ID 接口拿到包含加密 HId 的 JSON
        var html = request(this.host + id + sign);
        var realPlayUrl = '';
        try {
var json = JSON.parse(html);
// 解密 HId 字段即为最终的 m3u8/mp4 视频网络流直链
realPlayUrl = this.DubokuCrypto.decryptDataField(json.HId);
} catch (e) {
print("播放地址解密失败: " + e.message);
}
return JSON.stringify({
parse: 0, // 0 表示直连，电脑原生 VLC/Exo 内核会直接拉取数据硬解，速度极快
url: realPlayUrl,
header: {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
'Origin': 'https://w.duboku.io',
'Referer': 'https://w.duboku.io/'
}
});
}