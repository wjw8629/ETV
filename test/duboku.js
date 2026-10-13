/**
 * 独播库(Duboku) 桌面客户端 OKPlayer / FongMi Desktop 专用满血版
 * 完美修复：分类片库正常、多线程多源搜索无结果的问题
 */

// 1. 全局解密环境兼容垫片
if (typeof btoa === 'undefined') {
    globalThis.btoa = function (str) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        var output = '';
        for (var block, charCode, idx = 0, map = chars; str.charAt(idx | 0) || (map = '=', idx % 1); output += map.charAt(63 & block >> 8 - idx % 1 * 8)) {
            charCode = str.charCodeAt(idx += 3 / 4);
            block = block << 8 | charCode;
        }
        return output;
    };
}
if (typeof atob === 'undefined') {
    globalThis.atob = function (str) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
        var strStr = String(str).replace(/[=]+$/, '');
        for (var bc = 0, bs, fn, idx = 0, output = ''; fn = strStr.charAt(idx++); ~fn && (bs = bc % 4 ? bs * 64 + fn : fn, bc++ % 4) ? output += String.fromCharCode(255 & bs >> (-2 * bc & 6)) : 0) {
            fn = chars.indexOf(fn);
        }
        return output;
    };
}

// 2. 宿主隔离网络请求适配引擎
function safeFetchHtml(url, headers) {
    try {
        if (typeof local !== 'undefined' && typeof local.get === 'function') {
            return local.get(url, headers);
        }
        if (typeof req === 'function') {
            return req(url, { headers: headers }).content;
        }
        return request(url, { headers: headers });
    } catch (e) {
        return "[]";
    }
}

var rule = {
    title: '独播库[OKPlayer搜索修复版]',
    host: 'https://dbokutv.com',
    url: '/vodshow/fyclass-fyarea-fyby-fyclass-fylang----fypage---fyyear',
    searchUrl: '/vodsearch?wd=**',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'Referer': 'https://duboku.tv',
        'Connection': 'Keep-Alive'
    },
    timeout: 5000,
    class_name: '电影#电视剧#综艺#动漫#短剧#港剧#陆剧#日韩剧#台泰剧',
    class_url: '1#2#3#4#21#20#13#15#14',

    CryptoEngine: {
        a: function (len, seed, type) {
            var stringTable = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
            if (type === 88) {
                stringTable = "XYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW";
            }
            var result = '';
            for (var i = 0; i < len; i++) {
                var pseudoRandom = Math.abs(Math.sin(seed + i));
                var index = Math.floor(pseudoRandom * stringTable.length);
                result += stringTable.charAt(index);
            }
            return result;
        },

        b: function () {
            var currentSecs = Math.floor(Date.now() / 1000);
            var seedRandom = Math.abs(Math.sin(currentSecs));
            var iNextInt = Math.floor(seedRandom * 800000000) % 800000001;
            var strValueOf = Date.now().toString();
            var strPart = (100000000 + iNextInt).toString() + (900000000 - iNextInt).toString();
            var sb = '';
            var minLen = Math.min(strPart.length, strValueOf.length);
            for (var i = 0; i < minLen; i++) {
                sb += strPart.charAt(i) + strValueOf.charAt(i);
            }
            if (strPart.length > minLen) sb += strPart.substring(minLen);
            if (strValueOf.length > minLen) sb += strValueOf.substring(minLen);

            var strReplaceAll = btoa(sb).replace(/=/g, '.');
            var strA = this.a(60, 60 + currentSecs, 33);
            var strA2 = this.a(38, currentSecs + 38, 88);

            return "?sign=" + strA + "&ssid=" + strReplaceAll + "&token=" + strA2;
        },

        d: function (str) {
            if (!str) return '';
            var sb = '';
            var length = str.length;
            var i = 0;
            while (i < length) {
                var chunk = str.substring(i, Math.min(i + 10, length));
                sb += chunk.split('').reverse().join('');
                i += 10;
            }
            return atob(sb.replace(/\./g, '='));
        }
    },

    // 1. 首页加载
    home: function () {
        var signToken = this.CryptoEngine.b();
        var htmlContent = safeFetchHtml(this.host + '/home' + signToken, this.headers);
        var cardList = [];
        try {
            var rawJson = JSON.parse(htmlContent);
            rawJson.forEach(function (section) {
                if (section.VodList) {
                    section.VodList.forEach(function (v) {
                        cardList.push({
                            vod_id: rule.CryptoEngine.d(v.DId),
                            vod_name: v.Name,
                            vod_pic: rule.CryptoEngine.d(v.TnId),
                            vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                        });
                    });
                }
            });
        } catch (e) {}
        return JSON.stringify({ list: cardList });
    },

    // 2. 分类片库
    category: function (tid, pg, filter, extend) {
        var signToken = this.CryptoEngine.b();
        var area = (extend && extend.area) ? extend.area : '';
        var year = (extend && extend.year) ? extend.year : '';
        var by = (extend && extend.by) ? extend.by : '';
        var clazz = (extend && extend.class) ? extend.class : '';
        var lang = (extend && extend.lang) ? extend.lang : '';

        var subPath = "/vodshow/" + tid + "-" + area + "-" + by + "-" + clazz + "-" + lang + "----" + pg + "---" + year;
        var htmlContent = safeFetchHtml(this.host + subPath + signToken, this.headers);
        var cardList = [];
        try {
            var rawJson = JSON.parse(htmlContent);
            if (rawJson && rawJson.VodList) {
                rawJson.VodList.forEach(function (v) {
                    cardList.push({
                        vod_id: rule.CryptoEngine.d(v.DId),
                        vod_name: v.Name,
                        vod_pic: rule.CryptoEngine.d(v.TnId),
                        vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                    });
                });
            }
        } catch (e) {}
        
        return JSON.stringify({
            page: parseInt(pg),
            pagecount: 999,
            limit: 48,
            total: 9999,
            list: cardList
        });
    },

    // 3. 详情剧集
    detail: function (id) {
        var signToken = this.CryptoEngine.b();
        var htmlContent = safeFetchHtml(this.host + id + signToken, this.headers);
        var itemDetail = {};
        try {
            var rawJson = JSON.parse(htmlContent);
            var mediaTracks = [];
            if (rawJson.Playlist) {
                rawJson.Playlist.forEach(function (episode) {
                    var name = episode.EpisodeName;
                    var trueVId = rule.CryptoEngine.d(episode.VId);
                    mediaTracks.push(name + "$" + trueVId);
                });
            }

            itemDetail = {
                vod_id: id,
                vod_name: rawJson.Name,
                vod_pic: this.CryptoEngine.d(rawJson.TnId),
                vod_year: rawJson.ReleaseYear,
                vod_content: rawJson.Description,
                vod_actor: rawJson.Actor ? rawJson.Actor.join(', ') : '',
                vod_director: rawJson.Director,
                vod_play_from: '独播库超清源',
                vod_play_url: mediaTracks.join('#')
            };
        } catch (e) {}
        return JSON.stringify({ list: [itemDetail] });
    },

    // 4. 核心修复：完全对齐 OKPlayer 领域模型数据校验的全局搜索函数
    search: function (wd, quick) {
        var signToken = this.CryptoEngine.b();
        // 严格遵循原版 Java：wd 参数需要进行标准全局网络 URL 编码
        var searchUrl = this.host + '/vodsearch' + signToken + '&wd=' + encodeURIComponent(wd);
        var htmlContent = safeFetchHtml(searchUrl, this.headers);
        var searchResultList = [];
        try {
            var rawJson = JSON.parse(htmlContent);
            if (Array.isArray(rawJson)) {
                rawJson.forEach(function (v) {
                    searchResultList.push({
                        vod_id: rule.CryptoEngine.d(v.DId),
                        vod_name: v.Name,
                        vod_pic: rule.CryptoEngine.d(v.TnId),
                        vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                    });
                });
            }
        } catch (e) {}
        
        // 终极修复核心：包裹标准统一对象外壳，避免被 OKPlayer 判定为异常丢弃
        var outputResult = {
            code: 1,
            msg: "success",
            page: 1,
            pagecount: 1,
            limit: searchResultList.length,
            total: searchResultList.length,
            list: searchResultList
        };
        return JSON.stringify(outputResult);
    },

    // 5. 视频流直链提取
    play: function (flag, id, flags) {
        var signToken = this.CryptoEngine.b();
        var htmlContent = safeFetchHtml(this.host + id + signToken, this.headers);
        var decodedStreamingUrl = '';
        try {
            var rawJson = JSON.parse(htmlContent);
            decodedStreamingUrl = this.CryptoEngine.d(rawJson.HId);
        } catch (e) {}

        return JSON.stringify({
            parse: 0,
            url: decodedStreamingUrl,
            header: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
                'Origin': 'https://duboku.io',
                'Referer': 'https://duboku.io/'
            }
        });
    }
};
