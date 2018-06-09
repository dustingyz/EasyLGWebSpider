import json
import math
import os
import re
import sys
import time
import urllib
import urllib.parse
from urllib import request

if __name__ == '__main__':
    print('加载中文分词库...')

import jieba
import jieba.analyse as analyse

# import jieba.posseg as pseg

sys.path.append('../')


def str2url(string):
    url_safe_string = urllib.parse.quote(string)
    return url_safe_string


def progress2str(progress):
    full_char = '█'
    half_char = '▌'
    progress = int(round(progress, 2) * 100)
    fc = round(progress / 2)
    hc = progress & 1
    sc = 50 - fc - hc
    return ''.ljust(fc, full_char) + ''.ljust(hc, half_char) + ''.ljust(sc, ' ')


def salary_format(salary):
    salary = salary.strip().replace(' ', '')
    if salary.find('-') >= 0:
        splits = salary.split('-')
        average_salary = 0
        for i in list(map(lambda x: int(x.lower().replace('k', '000')), splits)):
            average_salary += i
        p = re.compile('000$')
        split = p.split(str(round(average_salary / 2)))
        if len(split) > 1:
            return split[0] + 'k'
        else:
            return str(round(int(split[0]) / 1000, 1)) + 'k'

    elif salary.find('k'):
        return salary


def digit_convert(d):
    if d.isdigit and 0 < int(d) < 10:
        return ['一', '二', '三', '四', '五', '六', '七', '八', '九'][int(d) - 1]


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
        print(('本次搜索到%d个职位' % total_count).center(50, '〓'))
        pagenum = int(math.ceil(total_count / 15))
        return pagenum

    def lagou_spider(self, key_word):
        keyword_url = str2url(key_word)
        self.debug_log(keyword_url)
        city_list = ['北京', '上海']
        # city_list = ['长沙']
        pardir_name = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        file_list = []
        for city in city_list:
            self.debug_log('current city is: %s' % city)
            print('正在保存{city}的职位'.format(city=city).center(50, '〓'))
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
            page_num = self.get_page_num(url, key_word, headers)
            if page_num:
                idx = 0

                filename = '{city}_{key_word}'.format(city=city, key_word=key_word)
                file_uri = os.path.pardir + os.path.sep + 'result' + os.path.sep + pardir_name + os.path.sep + city + os.path.sep + filename
                name = os.path.pardir + os.path.sep + 'result' + os.path.sep + pardir_name
                if not os.path.exists(name):
                    os.mkdir(name)
                name += os.path.sep + city
                if not os.path.exists(name):
                    os.mkdir(name)
                print('正在保存'.center(50, '〓'))

                with open(file_uri, 'wb') as f:
                    for i in range(page_num):
                        # if i == 0:
                        #     values = {'first': 'true', 'pn': '1', 'kd': key_word}
                        #     data = urllib.parse.urlencode(values).encode('utf-8')
                        # else:
                        values = {'first': 'true', 'pn': (i + 1), 'kd': key_word}
                        data = urllib.parse.urlencode(values).encode('utf-8')
                        req = request.Request(url, data, headers)
                        res = request.urlopen(req).read()

                        # print('正在保存第{page}页'.format(page=(i + 1)).center(50, '〓'), end='\n')
                        # print('\r' + '正在保存第{page}页'.format(page=(i + 1)).center(50, '〓'), end='')
                        progress = i / page_num
                        print('\r|' + progress2str(progress) + '| {p}%'.format(p=round(progress * 100)), end='')
                        sys.stdout.flush()
                        if self.debug_flg == 2:
                            print(res)
                        else:
                            json_data = json.loads(res, encoding='utf-8')
                            result_list = json_data['content']['positionResult']['result']
                            self.save_request_msg(result_list, f)
                        idx += 1
                    file_list.append(file_uri)
                    print('\r|' + progress2str(1) + '| 100%')
                    print('done')
        return file_list

    def save_request_msg(self, ls, file):
        for item in ls:
            if item['workYear'] is None:
                year_ = '不限'
            else:
                year_ = item['workYear']
                if year_.find('-') >= 0:
                    year_ = digit_convert(year_.split('-')[0]) + '年'

            msg = [item['education'],
                   # item['firstType'],
                   ','.join(item['positionLables']),
                   item['positionAdvantage'],
                   item['positionName'],
                   salary_format(item['salary']),
                   year_ + '工作经验']
            # print(msg)

            if self.debug_flg == 2:
                print(msg)
            else:
                """
                去除大小写造成的重复
                """
                s = str(msg).upper()
                change_dict = {
                    'JAVA': 'Java',
                    'PYTHON': 'Python',
                    'C++': 'C++',
                    'RUBY': 'Ruby',
                    'SCALA': 'Scala',
                    'KOTLIN': 'Kotlin',
                    'SWIFT': 'Swift',
                    'PHP': 'Php',
                    'MYSQL': 'MySQL',
                    'HADOOP': 'Hadoop',
                    'TENSORFLOW': 'TensorFlow',
                    'SPARK': 'Spark',
                    'LINUX': 'Linux',
                    'ANDROID': 'Android',
                    'IOS': 'iOS'
                }
                for key in change_dict:
                    s = s.replace(key, change_dict[key])
                self.debug_log(s, self.save_request_msg.__name__)
                file.write(s.encode('utf-8'))

    def debug_log(self, obj, method=''):
        if self.debug_flg:
            print(method, '\n', obj)


if __name__ == "__main__":
    flg = 0
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        flg = 1
    elif len(sys.argv) > 1 and sys.argv[1] == 'debug-p':
        flg = 2
    result_dir = os.path.pardir + os.path.sep + 'result'
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    keyword = input('请输入要爬取的关键词：')
    script = LagouScript(flg)
    file_list = script.lagou_spider(keyword)
    if len(file_list):
        jieba.load_userdict('../data/dict')
        read = b''
        all_sal = []
        for data in file_list:
            with open(data, 'rb') as f:
                read += f.read()
                p = re.compile('[0-9]+.?[0-9]?k')
                all_sal.extend(p.findall(read.decode()))
        text_rank = analyse.extract_tags(read, topK=100, withWeight=True,
                                         allowPOS=('ns', 'nr', 'r', 'n', 'nv', 'v', 'eng'))
        print(all_sal)
        for i in text_rank:
            print(i)
