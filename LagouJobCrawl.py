# -*- coding: utf-8 -*-
import requests
import browsercookie
import json
import time
import xlwt
import sys
from urllib.parse import urlencode

class LgCrawl(object):
    def __init__(self, city,job, pageNum):
        """

        :param job: 工作名字
        :param pageNum: 爬取页数
        """
        self.job = job
        self.city = urlencode({"city": city})
        self.excelName = u'%s-%s.xls' % (self.job, int(time.time()))
        self.pageNum = pageNum
        self.currentRow = 0
        self.book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.sheet = self.book.add_sheet(self.job, cell_overwrite_ok=True)

    def go(self):
        for page in range(self.pageNum):
            self.crawl(str(page + 1))

    def crawl(self, page):
        cookie_k = []
        cookie_v = []
        for cookie in browsercookie.chrome():
            if 'www.lagou.com'.rfind(str(cookie.domain)) != -1:
                # print("cookie:" + str(cookie.domain))
                # print("cookie:" + str(cookie.name))
                cookie_k.append(cookie.name)
                cookie_v.append(cookie.value)
        cookies = dict(zip(cookie_k, cookie_v))

        head = dict()
        head['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        head[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        head['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        head['Accept-Encoding'] = 'gzip, deflate, br'
        head['Accept-Language'] = 'zh-CN,zh;q=0.9'
        head['X-Requested-With'] = 'XMLHttpRequest'
        head['X-Anit-Forge-Token'] = 'None'
        head['X-Anit-Forge-Code'] = '0'
        head['X-Requested-With'] = 'XMLHttpRequest'
        head['Referer'] = 'https://www.lagou.com/jobs/list_%s?labelWords=&fromSearch=true&suginput='%self.job
        head['Origin'] = 'https://www.lagou.com'
        data = dict()
        if page == '1':
            data['first'] = 'true'
        else:
            data['first'] = 'false'
        data['pn'] = page
        data['kd'] = self.job
        print("cookies:" + str(cookies))
        print("header:" + str(head))
        print('data:' + str(data))
        resp = requests.post(
            url="https://www.lagou.com/jobs/positionAjax.json?px=default&%s&needAddtionalResult=false"%self.city,
            cookies=cookies, headers=head, data=data)
        print("resp:" + str(resp.content))
        # result = json.loads(resp.content)['content']['positionResult']['result']
        if 'success' in json.loads(resp.content):
            result = json.loads(resp.content)['content']['positionResult']['result']
            for r in result:
                self.writeExcel(r)
            # print("excelName:"+self.excelName)
            self.book.save(self.excelName)
        else:
            print("error:" + json.loads(resp.content)['msg'])

    def writeExcel(self, r):
        companyShortName = r['companyShortName']
        industryField = r['industryField']
        education = r['education']
        workYear = r['workYear']
        positionAdvantage = r['positionAdvantage']
        createTime = r['createTime']
        salary = r['salary']
        positionName = r['positionName']
        companySize = r['companySize']
        financeStage = r['financeStage']
        companyLabelList = r['companyLabelList']
        district = r['district']
        positionLables = r['positionLables']
        industryLables = r['industryLables']
        businessZones = r['businessZones']
        companyFullName = r['companyFullName']
        hitags = r['hitags']
        subwayline = r['subwayline']
        stationname = r['stationname']
        skillLables = r['skillLables']
        linestaion = r['linestaion']
        firstType = r['firstType']
        secondType = r['secondType']
        thirdType = r['thirdType']
        print(str(r) + ",currentRow:" + str(self.currentRow))

        self.sheet.write(self.currentRow, 0, companyShortName)
        self.sheet.write(self.currentRow, 1, industryField)
        self.sheet.write(self.currentRow, 2, education)
        self.sheet.write(self.currentRow, 3, workYear)
        self.sheet.write(self.currentRow, 4, positionAdvantage)
        self.sheet.write(self.currentRow, 5, createTime)
        self.sheet.write(self.currentRow, 6, salary)
        self.sheet.write(self.currentRow, 7, positionName)
        self.sheet.write(self.currentRow, 8, companySize)
        self.sheet.write(self.currentRow, 9, financeStage)
        self.sheet.write(self.currentRow, 10, companyLabelList)
        self.sheet.write(self.currentRow, 11, district)
        self.sheet.write(self.currentRow, 12, positionLables)
        self.sheet.write(self.currentRow, 13, industryLables)
        self.sheet.write(self.currentRow, 14, skillLables)
        self.sheet.write(self.currentRow, 15, companyFullName)
        self.sheet.write(self.currentRow, 16, businessZones)
        self.sheet.write(self.currentRow, 17, hitags)
        self.sheet.write(self.currentRow, 18, subwayline)
        self.sheet.write(self.currentRow, 19, stationname)

        self.sheet.write(self.currentRow, 20, linestaion)
        self.sheet.write(self.currentRow, 21, firstType)
        self.sheet.write(self.currentRow, 22, secondType)
        self.sheet.write(self.currentRow, 23, thirdType)
        self.sheet.write(self.currentRow, 24, companySize)
        self.currentRow += 1


###python LagouJobCrawl.py 城市 职业 页数开始爬取
if __name__ == "__main__":
    city=sys.argv[1]
    job=sys.argv[2]
    page=sys.argv[3]
    LgCrawl(city=city,job=job, pageNum=int(page)).go()
    
