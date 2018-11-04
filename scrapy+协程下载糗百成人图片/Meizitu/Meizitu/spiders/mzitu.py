# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

from Meizitu.items import MeizituItem


class MzituSpider(scrapy.Spider):
    name = 'qiubaichengren'
    allowed_domains = ['qiubaichengren.net']
    host = 'http://m.qiubaichengren.net/'
    url = 'http://m.qiubaichengren.net/{}.html'
    page = 2
    start_urls = [url.format(page)]

    def parse_item(self, response):
        print('parse=========', response.url)
        item = ItemLoader(item=MeizituItem(), response=response)
        item.add_value('url', response.url)
        item.add_value('page', response.url[len(self.host):].replace('/', '_'))
        # item.add_xpath('tags', "//ul[@id='article']/li/h2/a/text()")
        item.add_xpath('tags', "/html/body/div[2]/ul[@id='article']/li/h2/a/text()")
        item.add_xpath('image_urls', "//div[@class='pic']/a/img/@src")
        return item.load_item()

    def parse(self, response):
        while self.page < 100:
            yield scrapy.Request(self.url.format(self.page), callback=self.parse_item)
            self.page += 1

