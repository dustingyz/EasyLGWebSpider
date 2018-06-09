import json
import math
import os
import re
import sys
import time
import urllib
import urllib.parse
import uuid
from urllib import request

import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator

if __name__ == '__main__':
    print('加载中文分词库...')

import jieba
import jieba.analyse as analyse

sys.path.append('../')


def str2url(string):
    """
    返回 URL SAFE 参数
    :param string:
    :return:
    """
    url_safe_string = urllib.parse.quote(string)
    return url_safe_string


def progress2str(progress):
    """
    命令行进度条字符串生成，进度全长length 50
    :param progress:
    :return:
    """
    full_char = '█'
    half_char = '▌'
    progress = int(round(progress, 2) * 100)
    fc = round(progress / 2)
    hc = progress & 1
    sc = 50 - fc - hc
    return ''.ljust(fc, full_char) + ''.ljust(hc, half_char) + ''.ljust(sc, ' ')


def salary_format(salary):
    """
    把带k字的工资，转换成数字取平均值
    TODO 实际上做了无用功，应该改成去k求平均值，下次再改
    :param salary:
    :return:
    """
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
    """
    工作经验什么的，估计不会有超过10年的
    :param d:
    :return:
    """
    if d.isdigit and 0 < int(d) < 10:
        return ['一', '二', '三', '四', '五', '六', '七', '八', '九'][int(d) - 1]
    else:
        return '十'


class LagouSpider(object):

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
        # 用于文件夹命名，如果项目要扩大的话，下次有空改成date + uuid/random
        pardir_name = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.time_name = pardir_name
        file_list_out = []
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

            # 初始化请求头
            with open('..\\data\\http_headers', 'r', encoding='utf-8') as header_file:
                headers = json.load(header_file)
            headers['Content-Length'] = str(19 + len(keyword_url))
            headers['Referer'] = referer

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
                        values = {'first': 'true', 'pn': (i + 1), 'kd': key_word}
                        post_data = urllib.parse.urlencode(values).encode('utf-8')
                        req = request.Request(url, post_data, headers)
                        res = request.urlopen(req).read()

                        # print('正在保存第{page}页'.format(page=(i + 1)).center(50, '〓'), end='\n')
                        # print('\r' + '正在保存第{page}页'.format(page=(i + 1)).center(50, '〓'), end='')

                        # 进度条展示
                        progress = i / page_num
                        print('\r|' + progress2str(progress) + '| {p}%'.format(p=round(progress * 100)), end='')
                        sys.stdout.flush()

                        # 保存关键字到文件中
                        if self.debug_flg == 2:
                            print(res)
                        else:
                            # encoding_ = chardet.detect(res)['encoding']
                            # if encoding_ is not None:
                            #     self.debug_log(encoding_, 'enc')
                            #     json_data = json.loads(res, encoding=encoding_)
                            #     result_list = json_data['content']['positionResult']['result']
                            #     self.save_request_msg(result_list, f)
                            try:
                                json_data = json.loads(res, encoding='utf-8')
                                result_list = json_data['content']['positionResult']['result']
                                self.save_request_msg(result_list, f)
                            except Exception as e:
                                print(e)

                        idx += 1
                    file_list_out.append(file_uri)
                    print('\r|' + progress2str(1) + '| 100%')
                    print('done')
        return file_list_out

    def save_request_msg(self, ls, file):
        """
        获取岗位的关键信息并保存。
        :param ls: 岗位列表
        :param file: 储存文件
        :return:
        """
        for item in ls:
            if item['workYear'] is None:
                year_ = '不限'
            else:
                year_ = item['workYear']
                if year_.find('-') >= 0:
                    year_ = digit_convert(year_.split('-')[0]) + '年'

            """
            获取教育背景等情报
            """
            msg = [item['education'],
                   # item['firstType'],
                   ','.join(item['positionLables']),
                   item['positionAdvantage'],
                   item['positionName'],
                   salary_format(item['salary']),
                   year_ + '工作经验']

            if self.debug_flg == 2:
                print(msg)
            else:
                """
                去除大小写造成的重复
                """
                s = str(msg).upper()
                # change_dict = {
                #     'JAVA': 'Java',
                #     'PYTHON': 'Python',
                #     'C++': 'C++',
                #     'RUBY': 'Ruby',
                #     'SCALA': 'Scala',
                #     'KOTLIN': 'Kotlin',
                #     'SWIFT': 'Swift',
                #     'PHP': 'Php',
                #     'MYSQL': 'MySQL',
                #     'HADOOP': 'Hadoop',
                #     'TENSORFLOW': 'TensorFlow',
                #     'SPARK': 'Spark',
                #     'LINUX': 'Linux',
                #     'ANDROID': 'Android',
                #     'IOS': 'iOS'
                # }
                with open('..\\data\\name_map', 'r', encoding='utf-8') as name_map:
                    change_dict = json.load(name_map)

                for key in change_dict:
                    s = s.replace(key, change_dict[key])
                self.debug_log(s, self.save_request_msg.__name__)
                file.write(s.encode('utf-8'))

    def debug_log(self, obj, method=''):
        if self.debug_flg:
            print(method, '\n', obj)


def word_cloud_create(ls, salary, dir_name):
    """
    :param ls: 包含(词汇,词频）的数组
    :param salary: 工资
    :return:
    """
    res = 0
    for i in salary:
        res += float(i.split('K')[0])
    res = str(round(res / len(salary))) + 'k'
    ls.append((res, 1.0))

    confirm = input("是否使用默认背景颜色（白色）： Y or N >>>").lower()
    if confirm == 'y':
        rgbc = 'white'
    else:
        while True:
            rgbc = input('请输入 RGB 颜色,如: ff0088 >>>').lower().strip()
            m = re.compile('^[0-9a-f]{6}$').match(rgbc)
            if m is not None:
                break
            else:
                print('输入有误,16进制，最小值000000，最大值ffffff')
        rgbc = '#%s'.format(rgbc)

    word_dict = dict(zip([v[0] for v in ls], [v[1] for v in ls]))
    font_uri = '..\\data\\font.TTF'
    if not os.path.exists(font_uri):
        font_uri = 'C:\\Windows\\Fonts\\ARIALUNI.TTF'
    if not os.path.exists(font_uri):
        font_uri = 'C:\\Windows\\Fonts\\STZHONGS.TTF'

    mask_png = '..\\data\\mask.png'
    coloring = None
    color_func = None
    if os.path.exists(mask_png):
        img = Image.open(mask_png)
        coloring = np.array(img)
        color_func = ImageColorGenerator(coloring)
    cloud = WordCloud(background_color=rgbc, font_path=font_uri, mask=coloring)
    cloud.generate_from_frequencies(word_dict)
    cloud.recolor(color_func=color_func)
    filename = str(uuid.uuid4()) + '.png'
    dist_file = os.path.pardir + os.path.sep + 'result' + os.path.sep + dir_name + os.path.sep + filename
    cloud.to_file(dist_file)
    print('文件已生成，查看 %s' % os.path.abspath(dist_file))


if __name__ == "__main__":
    """
    启动参数
        debug：打印log
        debug-p：仅打印log，不保存文件
    """
    flg = 0
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        flg = 1
    elif len(sys.argv) > 1 and sys.argv[1] == 'debug-p':
        flg = 2
    result_dir = os.path.pardir + os.path.sep + 'result'
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    keyword = input('请输入要爬取的关键词>>>')

    spider = LagouSpider(flg)
    file_list = spider.lagou_spider(keyword)
    """
    读取保存成功的关键词文件列表
    """
    if len(file_list):
        jieba.load_userdict('..\\data\\dict')
        read = b''
        all_sal = []
        p = re.compile('[0-9]+.?[0-9]?K')
        for data in file_list:
            with open(data, 'rb') as f:
                read += f.read()
                all_sal.extend(p.findall(read.decode()))
        text_rank = analyse.extract_tags(read, topK=100, withWeight=True,
                                         allowPOS=('ns', 'nr', 'r', 'n', 'nv', 'v', 'eng'))
        spider.debug_log(all_sal, __name__)
        if spider.debug_flg:
            for i in text_rank:
                spider.debug_log(i, __name__)

        # print(all_sal)
        # print(len(all_sal))
        word_cloud_create(text_rank, all_sal, spider.time_name)
