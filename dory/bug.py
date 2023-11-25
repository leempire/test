# coding:utf-8
import html
import re
from .common import *
import requests
from contextlib import closing
import urllib


def download_file(url, filename, size=128):
    """视频url，储存文件名，下载节单位（KB）"""
    # 链接地址，获取内容赋值给r
    with closing(requests.get(url, stream=True)) as r:
        # 获取总长度
        total = int(r.headers['content-length']) / size / 1024
        progress = Progress(int(total))
        # 开始下载
        with open(filename, "wb") as f:
            n = 1  # 计数器
            for i in r.iter_content(chunk_size=size * 1024):
                # 写入文件
                f.write(i)
                n += 1
                # 是否刷新
                dt = progress.tick(n)
                if dt:
                    print('当前网速：{:>5.1f}MB/s'.format(10 * size / 1024 / dt), end='')
        progress.end()


def re_n(text):
    """处理含有大量\n的文本"""
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')
    return text.strip()


def _find(kw, text):
    direction = text.find(kw)
    if direction == -1:
        return None
    else:
        return Tag(_get_block(text, direction))


def _find_include(text, target, reverse=False):
    if reverse:
        index = text.rfind(target)
    else:
        index = text.find(target)
    if index == -1:
        return -1
    else:
        return index + len(target)


def _find_tag_name(text):
    return re.search(r'<(.*?)[ >]', text).group(1)


def _get_block(text, index):
    start = text[:index + 1].rfind('<')
    text = text[start:]
    tag_name = _find_tag_name(text)
    if text.find(f'</{tag_name}>') == -1:
        end = _find_include(text, '>')
        return text[:end]
    else:
        start_tag = '<' + tag_name
        end_tag = '</{}>'.format(tag_name)
        return _get_tail(text, start_tag, end_tag)


def _get_tail(text, start_tag, end_tag):
    index = 0
    count = 1
    while True:
        delta_index = _find_include(text[index:], end_tag)
        if delta_index == -1:
            return text[:index]
        index += delta_index
        if text[:index].count(start_tag) > count:
            count += 1
        else:
            return text[:index]


class Tag:
    def __init__(self, text=''):
        self.text = text

    def find(self, keyword):
        if type(keyword) == list:
            if len(keyword) > 1:
                return self.find(keyword[0]).find(keyword[1:])
            else:
                return self.find(keyword[0])
        return _find(keyword, self.text[:])

    def findall(self, keyword):
        text = self.text[:]
        result = []
        item = _find(keyword, text)
        while item:
            result.append(item)
            index = text.find(item.text) + len(item.text)
            text = text[index:]
            item = _find(keyword, text)
        return result

    def get_text(self, expel='', tag=''):
        if type(expel) == str:
            expel = list(expel)
        text = self.text
        for i in set(re.findall(r'<.*?>', text, re.S)):
            text = text.replace(i, tag)
        text = html.unescape(text)
        for i in expel:
            text = text.replace(i, '')
        return text

    def __getitem__(self, item):
        attribution = re.findall(r' (.{1,10}?)="(.*?)"', self.text.replace('\'', '"'), re.S)
        key = [k[0].strip() for k in attribution]
        if item in key:
            return attribution[key.index(item)][1]
        else:
            return None

    def __str__(self):
        return self.text


class Bug(Tag):
    """
    爬虫类
    参数：
    url
    encoding=utf-8
    timeout=3
    属性：
    text
    方法：
    get(url)
    find(keyword)
    save(filename)
    """

    def __init__(self, url='', encoding='utf-8', timeout=3, proxies=None):
        super().__init__()
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55',
        }
        self.html = None
        self.encoding = encoding
        self.timeout = timeout
        if type(proxies) == str:
            self.proxies = {
                'http:': 'http://' + proxies,
                'https:': 'https://' + proxies
            }
        else:
            self.proxies = proxies
        if url:
            self.get(url)

    def set_header(self, header):
        self.header = header

    def get(self, url):
        self.html = requests.get(url, headers=self.header, timeout=self.timeout, proxies=self.proxies)
        self.html.encoding = self.encoding
        self.text = self.html.text
        self.text = transform_encoding(self.text, self.encoding)

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.html.content)


class Search:
    """
    多线程爬虫框架
    方法：
    get_urls()
    browse(url)
    run(num=10)
    """
    got = []
    to_get = []
    error = []

    def __init__(self, dirname='./', filename='file.dory'):
        self.file = File(dirname, filename)
        self.load()

    def load(self):
        for i in ['got', 'to_get', 'error']:
            if i not in self.file:
                self.file[i] = []
        self.got = self.file['got']
        self.to_get = self.file['to_get']
        self.error = self.file['error']

    def thread(self):
        while self.to_get:
            item = self.to_get.pop(0)
            try:
                self.browse(item)
                self.got.append(item)
                print(f'\r剩余: {len(self.to_get)}', end='')
            except requests.exceptions.Timeout:
                self.to_get.append(item)
            except Exception as e:
                self.error.append(item)
                print(f'\r错误: {item} {e}')
            finally:
                self.save()

    def get_urls(self):
        pass

    def browse(self, item):
        pass

    def run(self, num=10):
        self.save()
        multi_task(num, self.thread)

    def save(self):
        self.file['error'] = self.error
        self.file['got'] = self.got
        self.file['to_get'] = self.to_get
        self.file.save()


if __name__ == '__main__':
    a = Tag('<a href="https://baidu.com"><h>你好</h></a>')
    print(a)
