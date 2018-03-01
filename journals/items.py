# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JournalsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pubmed_id = scrapy.Field() # unique on pubmed
    doi = scrapy.Field() # unique id that uses the issn number
    volume = scrapy.Field()
    issue = scrapy.Field()
    title = scrapy.Field()
    abstract = scrapy.Field()
    authors = scrapy.Field()
    pdf = scrapy.Field()
    subjects = scrapy.Field()
    page_url = scrapy.Field()
    canonical = scrapy.Field()
    journal_url = scrapy.Field()
    article_full_url = scrapy.Field()
    article_full_text_url = scrapy.Field()
    article_pdf_url = scrapy.Field()
    authors_emails = scrapy.Field()
    authors_institutions = scrapy.Field()
    publicatin_date = scrapy.Field()
    article_type = scrapy.Field()
    publisher = scrapy.Field()
    pisa = scrapy.Field()
    keywords = scrapy.Field()
    short_abstract = scrapy.Field()
    full_available_text = scrapy.Field()
    references = scrapy.Field()
    related_articles = scrapy.Field()
    access = scrapy.Field()
