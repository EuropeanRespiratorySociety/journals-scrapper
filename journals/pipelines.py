# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import requests
import json
import os

fileDir = os.path.dirname(os.path.realpath('__file__'))

with open(os.path.join(fileDir, 'config.json')) as f:
    config = json.load(f)


class JournalsPipeline(object):
    collection_name = 'journals'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if config.useMongo:
            if 'canonical' in item:
                self.upsert('canonical', item)
                return item
            elif 'pubmed_id' in item:
                self.upsert('pubmed_id', item)
                return item

        if config.useHttp:
            r = self.httpUpsert(item)
            print('Upsert operation: ', r.json())

        return item

    def upsert(self, key, item):
        self.db[self.collection_name].update(
            {
                key: item[key]
            },
            dict(item),
            upsert=True
        )

    def httpUpsert(self, item):
        r = '{}/webhook?type=save-journal-abstract&pw={}&force={}'.format(
            config['baseUrl'], config['pw'], config['force']
        )
        return requests.post(
            r,
            json=item
        )
