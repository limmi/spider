# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MeizituItem(scrapy.Item):
    # define the fields for your item here like:
    # 详情名称
    page = scrapy.Field()
    # 详情路径
    url = scrapy.Field()
    # 详情标签
    tags = scrapy.Field()
    # 图片列表
    image_urls = scrapy.Field()
    # 本地路径
    image_paths = scrapy.Field()
