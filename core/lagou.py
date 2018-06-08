import json
import time
import urllib
import urllib.parse
from urllib import request
import math
import sys
import os

sys.path.append('../')


def str2url(string):
    url_safe_string = urllib.parse.quote(string)
    return url_safe_string


class LagouScript(object):

    def __init__(self, debug_flg):
        self.debug_flg = debug_flg

    # 字符串转URL编码

    def get_page_num(self, url, key_word, headers):
        """
        获取职位数与页码
        :param url:
        :param key_word:
        :param headers:
        :return:
        """
        values = {'first': 'true', 'pn': '1', 'kd': key_word}
        data = urllib.parse.urlencode(values).encode('utf-8')
        req = request.Request(url, data, headers)
        json_result = request.urlopen(req).read()
        self.debug_log(json_result, self.get_page_num.__name__)
        total_count = int(json.loads(json_result.decode('utf-8'))["content"]["positionResult"]["totalCount"])
        self.debug_log(total_count, self.get_page_num.__name__)
        print('***本次搜索到%d个职位***' % total_count)
        pagenum = int(math.ceil(total_count / 15))
        return pagenum

    def lagou_spider(self, key_word):
        keyword_url = str2url(key_word)
        self.debug_log(keyword_url)
        # city_list = ['北京', '上海']
        city_list = ['长沙']
        pardir_name = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        for city in city_list:
            self.debug_log('current city is: %s' % city)
            print('正在保存{city}的职位'.format(city=city).center(50, '*'))
            city_url = str2url(city)
            url = ('https://www.lagou.com/jobs/positionAjax.json?px=default&city='
                   '{city_url}'
                   '&needAddtionalResult=false').format(city_url=city_url)
            referer = ('https://www.lagou.com/jobs/list_'
                       '{keyword_url}'
                       '?labelWords=&fromSearch=true&suginput=').format(keyword_url=keyword_url)
            self.debug_log(url)
            self.debug_log(referer)

            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN',
                'Cache-Control': 'no-cache',
                'Connection': 'Keep-Alive',
                'Content-Length': str(19 + len(keyword_url)),
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie': ('_ga=GA1.2.1886078051.1519979608; '
                           'LGUID=20180302163243-46c08eb6-1df4-11e8-998b-525400f775ce; '
                           'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1526871981,1527236505,1527503210; '
                           'index_location_city=%E5%8C%97%E4%BA%AC; '
                           'user_trace_token=20180528182604-478930c8-8ff6-415e-a224-7e0420f9a446; '
                           'X_HTTP_TOKEN=a15ff70fa1815b75f120dee33105d8b9; '
                           'LGSID=20180528182607-88293636-6261-11e8-8e50-5254005c3644; '
                           'PRE_UTM=; PRE_HOST=; '
                           'PRE_SITE=; '
                           'PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html'
                           '%3Fts%3D1527503164854%26serviceId%3Dlagou%26service%3Dhttp%25253A%25252F%25252F'
                           'www.lagou.com%25252Fjobs%25252F%26action'
                           '%3Dlogin%26signature%3D94D6FCA0DE46F8239E29F3E0F8B6867D; '
                           'LGRID=20180528182633-97cc535f-6261-11e8-ada5-525400f775ce; '
                           'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1527503237; _'
                           'gat=1; _gid=GA1.2.753663552.1527503230; '
                           'JSESSIONID=ABAAABAAADEAAFI1F7730EF42D4A55BD4F9D1207792A8A2; '
                           'TG-TRACK-CODE=index_search; SEARCH_ID=8fff00922bd94edfbfb554a19a1e2808'),
                'Host': 'www.lagou.com',
                'Origin': 'https://www.lagou.com',
                'Referer': referer,
                'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/60.0.3112.113 Safari/537.36'),
                'X-Anit-Forge-Code': '0',
                'X-Anit-Forge-Token': 'None',
                'X-HttpWatch-RID': '6479-10040',
                'X-Requested-With': 'XMLHttpRequest'
            }
            pagenum = self.get_page_num(url, key_word, headers)
            idx = 0
            for i in range(pagenum):
                if i == 0:
                    values = {'first': 'true', 'pn': '1', 'kd': key_word}
                    data = urllib.parse.urlencode(values).encode('utf-8')
                else:
                    values = {'first': 'true', 'pn': (i + 1), 'kd': key_word}
                    data = urllib.parse.urlencode(values).encode('utf-8')
                req = request.Request(url, data, headers)

                res = request.urlopen(req)
                filename = '{city}_{number}.txt'.format(city=city, number=idx)
                file_uri = os.path.pardir + os.path.sep + 'result' + os.path.sep + pardir_name + os.path.sep + city + os.path.sep + filename
                for line in res:
                    print('***正在保存第%d页***' % (i + 1))
                    if self.debug_flg == 2:
                        print(line)
                    else:
                        name = os.path.pardir + os.path.sep + 'result' + os.path.sep + pardir_name
                        if not os.path.exists(name):
                            os.mkdir(name)
                        name += os.path.sep + city
                        if not os.path.exists(name):
                            os.mkdir(name)
                        with open(file_uri, 'wb') as f:
                            f.write(line)

                idx += 1

    def debug_log(self, obj, method=''):
        if self.debug_flg:
            print(method, '\n', obj)


if __name__ == "__main__":
    flg = 1
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        flg = 1
    elif len(sys.argv) > 1 and sys.argv[1] == 'debug-p':
        flg = 2
    keyword = input('请输入要爬取的关键词：')
    script = LagouScript(flg)
    script.lagou_spider(keyword)
