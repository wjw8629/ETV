var rule = {
    title: '独播库[JS版]',
    host: 'https://dbokutv.com',
    url: '/vodshow/fyclass-fyarea-fyby-fyclass-fylang----fypage---fyyear',
    searchUrl: '/vodsearch?wd=**',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'Referer': 'https://duboku.tv'
    },
    timeout: 5000,
    class_name: '电影#电视剧#综艺#动漫#短剧#港剧#陆剧#日韩剧#台泰剧',
    class_url: '1#2#3#4#21#20#13#15#14',

    // 核心算法改写：等价替换 Java 中的 a(), b(), d() 签名与解密逻辑
    SignUtils: {
        randomString: function (len, seed, type) {
            let str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
            if (type === 88) str = "XYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW";
            let result = '';
            // 模拟 Java 的线性同余或伪随机，这里直接用简易随机
            for (let i = 0; i < len; i++) {
                result += str.charAt(Math.floor(Math.random() * str.length));
            }
            return result;
        },
        // 对应 Java 中的 b() 签名加密函数
        get_b_sign: function () {
            let now = Math.floor(Date.now() / 1000);
            let iNextInt = Math.floor(Math.random() * 800000000);
            let strValueOf = Date.now().toString();
            let str = (100000000 + iNextInt) + '' + (900000000 - iNextInt);
            let sb = '';
            let minLen = Math.min(str.length, strValueOf.length);
            for (let i = 0; i < minLen; i++) {
                sb += str.charAt(i) + strValueOf.charAt(i);
            }
            sb += str.substring(minLen) + strValueOf.substring(minLen);
            // 桌面端使用标准含有 btoa 的 JS 引擎进行 Base64 编码
            let strReplaceAll = btoa(sb).replace(/=/g, '.');
            let strA = this.randomString(60, 60 + now, 33);
            let strA2 = this.randomString(38, now + 38, 88);
            return `?sign=${strA}&ssid=${strReplaceAll}&token=${strA2}`;
        },
        // 对应 Java 中的 d() 翻转解密函数
        decode_d: function (str) {
            let sb = '';
            let length = str.length;
            let i = 0;
            while (i < length) {
                let chunk = str.substring(i, Math.min(i + 10, length));
                sb += chunk.split('').reverse().join('');
                i += 10;
            }
            // 还原 Base64 并解码
            let base64Str = sb.replace(/\./g, '=');
            return atob(base64Str);
        }
    },

    // 1. 首页推荐
    home: function () {
        let sign = this.SignUtils.get_b_sign();
        let html = request(this.host + '/home' + sign);
        let json = JSON.parse(html);
        let videos = [];
        json.forEach(item => {
            item.VodList.forEach(v => {
                videos.push({
                    vod_id: this.SignUtils.decode_d(v.DId),
                    vod_name: v.Name,
                    vod_pic: this.SignUtils.decode_d(v.TnId),
                    vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
                });
            });
        });
        return JSON.stringify({ list: videos });
    },

    // 2. 分类列表
    category: function (tid, pg, filter, extend) {
        let sign = this.SignUtils.get_b_sign();
        // 拼接成原源码 ://dbokutv.com 规则
        let url = this.host + `/vodshow/${tid}------${pg}---` + sign;
        let html = request(url);
        let json = JSON.parse(html);
        let videos = [];
        json.VodList.forEach(v => {
            videos.push({
                vod_id: this.SignUtils.decode_d(v.DId),
                vod_name: v.Name,
                vod_pic: this.SignUtils.decode_d(v.TnId),
                vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
            });
        });
        return JSON.stringify({ page: pg, pagecount: 999, limit: 48, total: 9999, list: videos });
    },

    // 3. 详情页（解析剧集列表）
    detail: function (id) {
        let sign = this.SignUtils.get_b_sign();
        let html = request(this.host + id + sign);
        let json = JSON.parse(html);
        
        let playList = [];
        json.Playlist.forEach(ep => {
            let epName = ep.EpisodeName;
            let vId = this.SignUtils.decode_d(ep.VId);
            // 拼装：单集名称\$视频ID
            playList.push(`${epName}$${vId}`);
        });

        let vod = {
            vod_id: id,
            vod_name: json.Name,
            vod_pic: this.SignUtils.decode_d(json.TnId),
            vod_year: json.ReleaseYear,
            vod_content: json.Description,
            vod_actor: json.Actor ? json.Actor.join(', ') : '',
            vod_director: json.Director,
            vod_play_from: '独播库',
            vod_play_url: playList.join('#')
        };
        return JSON.stringify({ list: [vod] });
    },

    // 4. 搜索功能
    search: function (wd, quick) {
        let sign = this.SignUtils.get_b_sign();
        let url = this.host + '/vodsearch' + sign + '&wd=' + encodeURIComponent(wd);
        let html = request(url);
        let json = JSON.parse(html);
        let videos = [];
        json.forEach(v => {
            videos.push({
                vod_id: this.SignUtils.decode_d(v.DId),
                vod_name: v.Name,
                vod_pic: this.SignUtils.decode_d(v.TnId),
                vod_remarks: v.Tag || (v.Rating ? v.Rating + '分' : '')
            });
        });
        return JSON.stringify({ list: videos });
    },

    // 5. 播放内容嗅探获取
    play: function (flag, id, flags) {
        let sign = this.SignUtils.get_b_sign();
        // 原 Java 里的 playerContent 会去请求接口拿加密的 HId
        let html = request(this.host + id + sign);
        let json = JSON.parse(html);
        let realUrl = this.SignUtils.decode_d(json.HId); // 解密出真实的流媒体播放地址

        return JSON.stringify({
            parse: 0, // 0 代表直链，电脑端直接硬解播放
            url: realUrl,
            header: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
                'origin': 'https://duboku.io',
                'referer': 'https://duboku.io/'
            }
        });
    }
};
