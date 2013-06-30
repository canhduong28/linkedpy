from scrapy import log
from twisted.enterprise import adbapi


from datetime import datetime
import MySQLdb.cursors

class LinkedinItemPipeline(object):
    def process_item(self, item, spider):
        return item

