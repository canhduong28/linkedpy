# -*- coding: utf-8 -*-
import re
import mmh3
from scrapy_redis.spiders import RedisSpider


class LinkedinTopicSpider(RedisSpider):
    name = 'linkedin_topic'
    allowed_domains = ['linkedin.com']
    redis_key = 'linkedin_topic_spider:start_urls'

    def parse(self, response):
        topic = response.xpath('//h1/text()').extract_first()
        yield {
            'topic_id': mmh3.hash(topic),
            'name': topic
        }

        skill_urls = response.xpath(
            '//a[@data-componentkey="statsskill"]/@href').extract()
        related_skill_urls = response.xpath(
            '//a[@data-componentkey="relatedTopics"]/@href').extract()
        skill_urls.extend(related_skill_urls)
        for skill_url in skill_urls:
            skill_url = re.sub(r'\?trk=.+', '', skill_url)
            yield {
                'url': skill_url
            }
