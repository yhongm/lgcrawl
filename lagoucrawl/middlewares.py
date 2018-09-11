# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
import random
from scrapy import signals

from lagoucrawl.settings import USER_AGENT_POOL

from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import logging
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from os import path
import csv
from itertools import islice

ips = []


def input_ips():
    dir = path.dirname('.')
    print("dir:" + path.abspath(dir))
    print("start ips.length")
    with open(path.join(dir, 'lagoucrawl/ip.csv'), 'r') as f:
        lines = csv.reader(f)
        for line in islice(lines, 1, None):
            # print("line.length:" + str(len(line)))
            if len(line) == 1:
                # print("line:" + str(line[0]))
                ips.append(line[0])

        print("ips.length:" + str(len(ips)))


class MyRetryMiddleware(RetryMiddleware):
    logger = logging.getLogger(__name__)

    def __init__(self, settings):

        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        input_ips()
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def delete_proxy(self, proxy):
        if proxy:
            print("proxy,before ip:" + proxy)
            proxy = proxy[7:]
            print("proxy,after ip:" + proxy)
            ips.remove(proxy)
            print("proxy delete ip length:" + str(len(ips)))

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        logging.info("response.status:" + str(response.status))
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            self.delete_proxy(request.meta.get('proxy', False))
            time.sleep(random.randint(10, 12))
            self.logger.warning('返回值异常, 进行重试...')
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            self.delete_proxy(request.meta.get('proxy', False))
            time.sleep(random.randint(3, 5))
            self.logger.warning('连接异常, 进行重试...')

            return self._retry(request, exception, spider)

    def spider_opened(self, spider):
        spider.logger.info('start Spider opened: %s' % spider.name)



class MyUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        thisua = random.choice(USER_AGENT_POOL)
        request.headers.setdefault('User-Agent', thisua)


class MyproxiesSpiderMiddleware(HttpProxyMiddleware):

    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        thisip = random.choice(ips)
        print("this is ip:" + thisip)
        request.meta["proxy"] = "http://" + thisip


class LagoucrawlSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class LagoucrawlDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
