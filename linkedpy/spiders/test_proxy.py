from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
 
class TestSpider(CrawlSpider):
    name = "test"
    domain_name = "whatismyip.com"
    # The following url is subject to change, you can get the last updated one from here :
    # http://www.whatismyip.com/faq/automation.asp
    start_urls = ["http://automation.whatismyip.com/n09230945.asp"]
 
    def parse(self, response):
        open('test.html', 'wb').write(response.body)
