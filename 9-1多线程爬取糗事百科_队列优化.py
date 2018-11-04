import json
from queue import Queue
from threading import Thread, Lock
import requests
from lxml import etree


class CrawlThread(Thread):
    def __init__(self, name, page_queue, data_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.page_queue = page_queue
        self.data_queue = data_queue

    def run(self):
        while not self.page_queue.empty():
            page = self.page_queue.get()
            url = 'https://www.qiushibaike.com/8hr/page/' + str(page) + '/'
            print('{}正在爬取: {}'.format(self.name, url))
            response = requests.get(url)
            data = response.content
            self.data_queue.put(data)
            self.page_queue.task_done()  # 利用队列的 tesk_done 替换线程的join
            print('{} 爬取结束'.format(url))


class ParseThread(Thread):
    def __init__(self, name, data_queue, file, lock):
        super(ParseThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.file = file
        self.lock = lock

    def run(self):
        while not self.data_queue.empty():
            content = self.data_queue.get()
            print('{} 开始解析 '.format(self.name, ))
            print('{} 解析结束 数量{}'.format(self.name, self.parse_data(content)))
            self.data_queue.task_done()

    def parse_data(self, content):
        html = etree.HTML(content)
        node_list = html.xpath('//div[contains(@id,"qiushi_tag")]')
        qiushi_list = []

        for node in node_list:
            # 用户头像链接,返回的是列表
            user_image = node.xpath('./div[@class="author clearfix"]/a/img/@src')
            # 用户昵称，返回的是列表
            user_name = node.xpath('./div/a/h2/text()')
            # 段子内容，返回是列表
            content = node.xpath('./a/div[@class="content"]/span/text()')
            # 点赞次数
            dianzhang = node.xpath('./div/span/i[@class="number"]/text()')
            # 评论次数
            comment = node.xpath('./div/span/a[@class="qiushi_comments"]/i/text()')
            if user_image:
                user_image = user_image[0]
            if user_name:
                user_name = user_name[0]
            if content:
                content = "".join(content)
            if dianzhang:
                dianzhang = dianzhang[0]
            if comment:
                comment = comment[0]

            # 3.封装成字典，并且添加到列表
            item = {}
            item["user_image"] = user_image
            item["user_name"] = user_name
            item["content"] = content
            item["dianzhang"] = dianzhang
            item["comment"] = comment

            qiushi_list.append(item)
            with self.lock:
                str_json = json.dumps(item, ensure_ascii=False) + '\n'
                self.file.write(str_json)
        return len(qiushi_list)


def main():
    # 1. 采集数据
    # 将10页的数据,存入到数据队列
    page_queue = Queue()
    data_queue = Queue()
    [page_queue.put(n) for n in range(1, 11)]
    crawl_thread_names = ['采集线程1', '采集线程2', '采集线程3']
    crawl_threads = []
    for name in crawl_thread_names:
        thread = CrawlThread(name, page_queue, data_queue)  # ready
        thread.start()  # running
        crawl_threads.append(thread)
    # 等待采集完毕
    page_queue.join()

    # 2. 解析数据
    # 将数据队列中的数据解析完毕,存入json文件
    lock = Lock()
    parse_thread_names = ['解析线程1', '解析线程2', '解析线程3']
    parse_threads = []

    file = open('嗅事百科.json', 'a', encoding='utf-8')

    for name in parse_thread_names:
        thread = ParseThread(name, data_queue, file, lock)
        thread.start()
        parse_threads.append(thread)
    # 等待子线程解析完毕
    data_queue.join()
    # 关闭文件
    with lock:
        file.close()


if __name__ == '__main__':
    main()
