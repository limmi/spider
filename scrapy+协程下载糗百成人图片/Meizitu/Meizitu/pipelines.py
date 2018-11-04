# -*- coding: utf-8 -*-

# 1. 在管道开始的时候创建 -- 协程池列表
# 2. 将下载图片任务，单独定义一个函数，
#    每一个请求转为协程任务，并加入协程池列表
# 3. 管道结束之前的时候 -- 堵塞协程池

from gevent import monkey

monkey.patch_all()
import gevent
import json
import os
import requests


def download_image(path, url, name):
    if not os.path.exists(path):
        os.makedirs(path)
    print('下载图片------', url)
    response = requests.get(url)
    with open(path + name, 'wb') as f:
        [f.write(block) for block in response.iter_content(2048) if block]
    print('下载完成', url)


class MeizituPipeline(object):
    def open_spider(self, spider):
        print('open_spider----', spider.name)
        # 创建协程池
        self.file = open('糗事成人.json', 'w', encoding='utf-8')
        self.gevent_pools = []

    def close_spider(self, spider):
        self.file.close()
        # 堵塞协程池
        print(len(self.gevent_pools))
        gevent.joinall(self.gevent_pools)
        print('close_spider----', spider.name)

    def process_item(self, item, spider):
        print('保存图片----------')
        image_paths = []
        dir_path = '{}/{}/{}/'.format(
            os.path.dirname(os.path.realpath('__file__')),
            spider.name,
            item['page'][0].replace('.', '_')
        )
        for n, image_url in enumerate(item['image_urls']):
            name = item['tags'][n] + '-' + image_url.split('/')[-1]
            image_path = dir_path + name
            image_paths.append(image_path)

            # 创建协程任务，加入协程池
            mission = gevent.spawn(download_image, dir_path, image_url, name)
            self.gevent_pools.append(mission)
        print('当前线程数量',len(self.gevent_pools))
        item['image_paths'] = image_paths
        self.file.write(json.dumps(dict(item), ensure_ascii=False) + '\n')
        return item
