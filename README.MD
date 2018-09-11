# scrapy+splash  爬取拉勾全站职位信息
## 本项目代码尽供学习使用
## 使用方法:
<ol>
  <li>首先根据对应系统平台安装docker</li>
  <li>sudo docker pull scrapinghub/splash 安装splash</li>
  <li>sudo docker run -p 8050:8050 -p 8051:8051 scrapinghug/splash 启动splash</li>
  <li>cd 到爬虫目录下，执行scrapy crawl lgcrawl -o jobs_all.csv 命令启动爬虫</li>
<ol>
  
<br/>



