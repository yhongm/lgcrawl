# -*- coding: utf-8 -*-
import random

import scrapy
import time
from scrapy_splash import SplashRequest

from lagoucrawl.items import LagoucrawlItem
from scrapy.conf import settings
import browsercookie

lua_script = '''
          function main(splash)
             print("cookies.type:",type(splash.args.cookies))
             for k, v in pairs(splash.args.cookies) do
                 
                  local cookie = splash:add_cookie{k, v,"/",domain=".lagou.com"}
                  print("add after cookie:",cookie)
             end
             splash:init_cookies(splash:get_cookies())
             splash:go(splash.args.url)
             
             splash:wait(2)
             
             return splash:html()
          end
          '''


class LgcrawlSpider(scrapy.Spider):
    name = 'lgcrawl'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']
    baseurl = "https://www.lagou.com/zhaopin/"
    meta = settings['META']
    splash_args = {}
    cookies = {}

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.start_parse_job)

    def start_parse_job(self, response):
        url_jobs = response.css('.sidebar .mainNavs .menu_box .menu_sub dd a.curr')

        cookie_k = []
        cookie_v = []
        for cookie in browsercookie.chrome():
            if ('www.lagou.com'.rfind(str(cookie.domain)) != -1):
                # print("cookie:" + str(cookie.domain))
                # print("cookie:" + str(cookie.name))
                cookie_k.append(cookie.name)
                cookie_v.append(cookie.value)
        self.cookies = dict(zip(cookie_k, cookie_v))

        headers = {
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',

        }
        splash_args = {
            'wait': 5,
            "http_method": "GET",
            # "images":0,

            "render_all": 1,
            "headers": headers,
            'lua_source': lua_script,
            "cookies": self.cookies,

        }
        self.splash_args = splash_args

        for url_job in url_jobs:
            classify_href = url_job.xpath('@href').extract_first()
            classify_name = url_job.xpath('text()').extract_first()
            url = classify_href + "1/?filterOption=2"

            yield SplashRequest(url=url, endpoint='execute',
                                meta={'classify_name': classify_name, 'classify_href': classify_href},
                                callback=self.parse_total_page,
                                dont_filter=True,
                                args=splash_args, cache_args=['lua_source'])

    def parse_total_page(self, response):
        total_page = '0'
        try:
            total_page = response.xpath('//*[@id="order"]/li/div[4]/div/span[2]/text()').extract_first()
            print("total_page:" + total_page)
        except Exception as e:
            total_page = '0'
        classify_href = response.meta['classify_href']
        for i in range(1, int(total_page) + 1):
            url = classify_href + "/%s/?filterOption=2" % i
            if i % random.randint(1, 9) == 0:  # 随机延时
                time.sleep(random.randint(1, 2))
            yield SplashRequest(url=url, endpoint='execute', meta={'classify_name': response.meta['classify_name']},
                                callback=self.parse_item,
                                dont_filter=True,
                                args=self.splash_args, cache_args=['lua_source'])

    def parse_item(self, response):

        list = response.xpath('//*[@class="con_list_item default_list"]')
        print("parse,response.length:" + str(len(response.text)) + ",list.length:" + str(
            len(list.extract())) + ",url:" + response.url)
        title = response.xpath('/html/head/title/text()').extract_first()
        if len(list.extract()) == 0:
            print("list 0,title:%s" % title)
        else:
            print("list %d title %s" % (len(list), title))
        for li in list:
            position = li.xpath('./div[@class="list_item_top"]/div[@class="position"]')
            job_name = position.xpath('./div[@class="p_top"]/a/h3/text()').extract_first()
            job_info_url = position.xpath('./div[@class="p_top"]/a/@href').extract_first()
            money = position.xpath('./div[@class="p_bot"]/div[@class="li_b_l"]/span/text()').extract_first()
            company = li.xpath(
                './div[@class="list_item_top"]/div[@class="company"]/div[@class="company_name"]/a/text()').extract_first()

            yield SplashRequest(url=job_info_url, endpoint='execute',
                                meta={'job_name': job_name, 'money': money, 'company': company,
                                      'classify_name': response.meta['classify_name']},
                                callback=self.parse_info, dont_filter=True,
                                args=self.splash_args, cache_args=['lua_source'])

    def parse_info(self, response):
        item = LagoucrawlItem()
        item['job_name'] = response.meta['job_name']
        item['money'] = response.meta['money']
        item['company'] = response.meta['company']
        item['classify_name'] = response.meta['classify_name']
        item['advantage'] = str(response.css('.job-advantage p::text').extract())
        item['requirements'] = str(response.css('.job_bt p::text').extract())
        item['info'] = str(response.css('.position-head .position-content .position-content-l .job_request p').xpath(
            './span/text()').extract())

        print('item:' + str(item))
        yield item
