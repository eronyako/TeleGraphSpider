#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Subj: PyCharm
# @File: TeleGraphSpider.py
# @Date: 2022/9/5 13:14

import os
import sys
import re
import requests
from bs4 import BeautifulSoup

url_root = 'https://telegra.ph/'
headers_def = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
title_re = 'class="tl_article_content"><h1>(.*?)<br></h1><address>'
img_re = '<img src="/(.*?)">'


def get_graph_url():
    # 取得 url 文件路径
    try:
        file_name = sys.argv[1]
    except IndexError:
        print('未拖动文件打开，尝试 urls.txt')
        if os.path.isfile(os.path.join(os.getcwd(), 'urls.txt')):
            file_name = os.path.join(os.getcwd(), 'urls.txt')
        else:
            raise FileNotFoundError('未找到 urls.txt')

    # 读取 url 文件生成列表
    with open(file_name, 'r', encoding='UTF-8') as f:
        urls = f.readlines()
    urls = list(map(lambda v: v.strip(), urls))
    while '' in urls:
        urls.remove('')
    return urls


# 正则式方式获取名称与图片链接
def get_pic_url_re(url: str, headers: dict):
    # 获取页面内容
    res = requests.get(url=url, headers=headers).text
    # 取得标题
    title = re.findall(title_re, res, re.S)[0]
    # 找到图片名称
    url_list = re.findall(img_re, res, re.S)
    # 将名称加上前缀转为 url
    url_list = list(map(lambda v: url_root + v, url_list))
    return title, url_list


# bs4 方式获取名称与图片链接
def get_pic_url_bs4(url: str, headers: dict):
    # 获取页面内容
    res = BeautifulSoup(requests.get(url=url, headers=headers).text, 'lxml')
    # 取得标题
    title = res.select('.tl_article_header > h1')[0].text
    # 找到图片名称
    url_list_soup = res.select('#_tl_editor > img')
    url_list = []
    for v in url_list_soup:
        url_list.append(v['src'].strip('/'))
    # 将名称加上前缀转为 url
    url_list = list(map(lambda i: url_root + i, url_list))
    return title, url_list


def get_img(title: str, url_list: list, headers: dict, path: str):
    # 判断是否出现重名目录
    if not os.path.exists(os.path.join(path, title)):
        os.mkdir(os.path.join(path, title))
        # 通过 i 计数，使图片名称序列化
        i = 0
        for v in url_list:
            i += 1
            # 取得图片内容
            img = requests.get(v, headers=headers).content
            # 整理图片名
            img_name = format(i, '03d') + '.' + v.split('.')[-1]
            # 写入硬盘
            with open(os.path.join(path, title, img_name), 'wb') as f:
                f.write(img)
    else:
        # 若重名，则不保存
        print(f'文件夹已存在：{title}')


def main():
    # 创建 telegraph_lib 目录
    lib_path = os.path.join(os.getcwd(), 'telegraph_lib')
    if not os.path.exists(lib_path):
        os.mkdir(lib_path)

    graph_list = get_graph_url()
    # 对每个 telegraph url 列表循环获取
    for v in graph_list:
        # 取得名字和图片列表
        hon_name, img_list = get_pic_url_re(v, headers_def)
        # 获取图片
        get_img(hon_name, img_list, headers_def, lib_path)


if __name__ == '__main__':
    main()
