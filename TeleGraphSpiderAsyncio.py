#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Subj: PyCharm
# @File: TeleGraphSpiderAsyncio.py
# @Date: 2022/9/6 15:42

import os
import sys
import json

import asyncio
import aiohttp
from lxml import etree

url_root = 'https://telegra.ph/'
headers_def = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}

lib_dir = 'telegraph_lib'

pic_urls_dict = dict()


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


# xPath 方式获取名称与图片链接
async def get_pic_url(url: str, headers: dict):
    # 获取页面内容
    async with aiohttp.ClientSession() as session:
        async with await session.get(url=url, headers=headers) as res:
            res_tree = etree.HTML(await res.text())
            # 取得标题, '/'表示根层级或一个层级，'//'表示从任意层级开始或多个层级,'[i]'可表示索引定位，从 1 开始
            # 取得文字时，可使用 'xpath/text()' 取得直系文本，使用 'xpath//text()' 取得所有文本
            title = res_tree.xpath('/html/body//main/header/h1/text()')[0]
            # 找到图片名称
            url_list = res_tree.xpath('//article[@id="_tl_editor"]/img/@src')
            # 将名称加上前缀转为 url
            url_list = list(map(lambda i: url_root + i.strip('/'), url_list))
            return title, url_list


def get_pic_url_callback(task):
    pic_urls_dict[task.result()[0]] = task.result()[1]
    print('地址获取完成：', task.result()[0])


async def get_img(title: str, url_list: list, headers: dict, path: str):
    # 判断是否出现重名目录
    if not os.path.exists(os.path.join(path, title)):
        os.mkdir(os.path.join(path, title))
        # 通过 i 计数，使图片名称序列化
        i = 0
        list_len = len(url_list)
        for v in url_list:
            i += 1
            # 取得图片内容
            async with aiohttp.ClientSession() as session:
                async with await session.get(url=v, headers=headers) as res:
                    img = await res.read()
                    # 整理图片名
                    img_name = format(i, '03d') + '.' + v.split('.')[-1]
                    # 写入硬盘
                    with open(os.path.join(path, title, img_name), 'wb') as f:
                        f.write(img)
            print(title, ': 已完成 [', i, '/', list_len, ']')
    else:
        # 若重名，则不保存
        print(f'文件夹已存在：{title}')


def main():
    # 创建 lib 目录
    lib_path = os.path.join(os.getcwd(), lib_dir)
    if not os.path.exists(lib_path):
        os.mkdir(lib_path)

    # 载入需要爬取的网址
    graph_list = get_graph_url()

    # 异步获取 名称 与 url
    get_pic_url_tasks = []
    # 创建事件循环
    get_pic_url_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(get_pic_url_loop)
    for v in graph_list:
        # 创建携程
        c = get_pic_url(v, headers_def)
        # 将任务添加到循环中
        get_pic_url_task = get_pic_url_loop.create_task(c)
        get_pic_url_task.add_done_callback(get_pic_url_callback)
        get_pic_url_tasks.append(get_pic_url_task)

    # 执行异步获取图片 url
    get_pic_url_loop.run_until_complete(asyncio.wait(get_pic_url_tasks))

    # 保存 url 数据为 json
    with open(os.path.join(lib_path, 'pic_urls.json'), 'w', encoding='UTF-8') as f:
        json.dump(pic_urls_dict, f, ensure_ascii=False, indent=4)

    # 对每个 telegraph url 列表循环获取
    get_img_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(get_img_loop)
    get_img_tasks = []
    for v in pic_urls_dict:
        # 创建携程
        c = get_img(v, pic_urls_dict[v], headers_def, lib_path)
        # 将任务添加到循环中
        get_img_task = get_pic_url_loop.create_task(c)
        get_img_tasks.append(get_img_task)

    # 执行异步获取图片数据
    get_pic_url_loop.run_until_complete(asyncio.wait(get_img_tasks))
    print('已全部下载完成')


if __name__ == '__main__':
    main()
