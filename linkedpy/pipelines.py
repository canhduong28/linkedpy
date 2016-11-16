# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from twisted.internet.threads import deferToThread

from scrapy_redis import connection

from linkedpy import settings
from linkedpy.models import Topics, db_connect, create_topics_table


class LinkedinPipeline(object):
    """LinkedinPipeline pipeline for storing scraped items in the database"""

    def __init__(self, redis_conn):
        self.redis_conn = redis_conn
        engine = db_connect()
        create_topics_table(engine)
        self.Session = sessionmaker(bind=engine)

    @classmethod
    def from_settings(cls, settings):
        params = {
            'redis_conn': connection.from_settings(settings)
        }
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        if 'topic_id' in item:
            return deferToThread(self.process_topic_item, item, spider)
        return deferToThread(self.process_url_item, item, spider)

    def process_url_item(self, item, spider):
        """Push URLs into the Redis queue"""

        self.redis_conn.rpush(spider.redis_key, item['url'])
        return item

    def process_topic_item(self, item, topic):
        """Save topics in the database"""

        session = self.Session()
        topic = Topics(**item)
        try:
            session.add(topic)
            session.commit()
        except IntegrityError, e:
            session.rollback()
            if 'Duplicate' in e.message:
                pass
            else:
                raise
        finally:
            session.close()

        return item
