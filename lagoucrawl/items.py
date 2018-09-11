# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LagoucrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_name = scrapy.Field()
    money = scrapy.Field()
    company = scrapy.Field()
    classify_name = scrapy.Field()
    advantage = scrapy.Field()
    requirements = scrapy.Field()
    info = scrapy.Field()
    pass
