# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from journals.items import JournalsItem
from datetime import datetime

import json
import os
from urllib.parse import urlparse
from urllib.parse import parse_qsl

# http://erj.ersjournals.com/sitemap.xml
# http://err.ersjournals.com/sitemap.xml
# http://breathe.ersjournals.com/sitemap.xml
# http://openres.ersjournals.com/sitemap.xml

fileDir = os.path.dirname(os.path.realpath('__file__'))
with open(os.path.join(fileDir, 'config.json')) as f:
    config = json.load(f)


class ArticleSpider(CrawlSpider):
    name = 'article'
    allowed_domains = config.domains
    start_urls = [
        'http://erj.ersjournals.com/content/by/year/1988',
        'http://erj.ersjournals.com/content/by/year/2018',
        'http://breathe.ersjournals.com/content/by/year/2004'
        'http://breathe.ersjournals.com/content/by/year/2018'
        'http://err.ersjournals.com/content/by/year/2005',
        'http://err.ersjournals.com/content/by/year/2018',
        'http://openres.ersjournals.com/content/by/year/2015',
        'http://openres.ersjournals.com/content/by/year/2018'
    ]

    rules = (
        Rule(LinkExtractor(allow=('.*', ), deny=(
            r'\/by\/section\/Cell',
            r'external-ref?',
            r'%7Bopenurl%7D?',
            r'{openurl}',
            r'user\/login',
            r'by\/section',
            r'lookup',
            r'lookup\/google-scholar',
            r'lookup\/ijlink',
            r'lens\/',
            r'keyword',
            r'panels_ajax_tab',
            r'\.pdf',
            r'\.zip',
            r'\.full.print',
            r'\.print',
            r'\.DC1',
            r'\.DC2',
            r'\.DC3',
            r'\.DC4',
            r'\.DC5',
            r'\.DC6',
            r'\.full',
            r'\.full\.pdf',
            r'\.figures-only',
            r'\.article-info',
            r'\.abstract',
            r'\.full\.txt',
            r'\.full-text\.print',
            r'\.twitter',
            r'highwire\/payment',
            r'highwire\/citation',
            r'highwire\/powerpoint',
            r'powerpoint',
            r'login',
            r'logout',
            r'expansion', )), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        i = {}
        i['page_url'] = response.url
        canonical = self.stringify(response.xpath('//link[@rel="canonical"]/@href'))
        i['journal_url'] = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(response.url))
        i['journal_name'] = self.stringify(response.xpath('//meta[@name="citation_journal_title"]/@content'))
        i['article_full_url'] = self.stringify(response.xpath('//meta[@name="citation_full_html_url"]/@content'))
        i['article_full_text_url'] = self.stringify(response.xpath('//meta[@name="citation_full_html_url"]/@content'))
        i['article_pdf_url'] = self.stringify(response.xpath('//meta[@name="citation_pdf_url"]/@content'))
        i['authors'] = response.xpath('//meta[@name="citation_author"]/@content').extract()
        i['authors_institutions'] = self.setInstitutions(response.xpath('//meta[@name="citation_author_institution"]/@content').extract())
        i['authors_emails'] = response.xpath('//meta[@name="citation_author_email"]/@content').extract()
        i['publication_date'] = self.stringify(response.xpath('//meta[@name="citation_publication_date"]/@content'))
        i['article_type'] = self.stringify(response.xpath('//meta[@name="citation_article_type"]/@content'))
        i['related_articles'] = response.xpath('//meta[@name="DC.Relation"]/@content').extract()
        i['access'] = self.stringify(response.xpath('//meta[@name="DC.AccessRights"]/@content'))
        i['pisa'] = self.stringify(response.xpath('//meta[@name="HW.pisa"]/@content'))
        i['subjects'] = self.cleanUrls(response.xpath('//a[@class="highlight"]'))
        i['title'] = self.stringify(response.xpath('//meta[@name="citation_title"]/@content'))
        i['abstract'] = self.stringify(response.xpath('//meta[@name="og:description"]/@content'))
        i['short_abstract'] = self.stringify(response.xpath('//meta[@name="citation_abstract" and @scheme="short"]/@content'))
        i['full_available_text'] = ''.join(response.xpath('//div[@class="section"]/p').extract())
        i['keywords'] = response.xpath('//ul[@class="kwd-group"]/li/a/text()').extract()
        i['references'] = self.cleanRef(response.xpath('//div[@class="section ref-list"]/ol/li/div'))
        pid = self.stringify(response.xpath('//meta[@name="citation_pmid"]/@content'))
        vol = self.stringify(response.xpath('//meta[@name="citation_volume"]/@content'))
        iss = self.stringify(response.xpath('//meta[@name="citation_issue"]/@content'))
        doi = self.stringify(response.xpath('//meta[@name="DC.Identifier"]/@content'))
        publisher = self.stringify(response.xpath('//meta[@name="DC.Publisher"]/@content'))
        i['scrapedOn'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        if '/early/' not in canonical and len(canonical) > 0:
            i['canonical'] = canonical

        if publisher != '':
            i['publisher'] = publisher

        if len(doi) > 1 and doi != '':
            i['doi'] = doi

        if str.isdigit(pid):
            i['pubmed_id'] = int(pid)

        if str.isdigit(vol):
            i['volume'] = int(vol)

        if str.isdigit(iss):
            i['issue'] = int(iss)

        return i

    def cleanRef(self, strings):
        ref = []
        for s in strings:
            article_title = self.stringify(s.xpath('.//div/cite/span[@class="cit-article-title"]/text()'))
            publication_name = self.stringify(s.xpath('.//div/cite/span[@class="cit-publ-name"]/text()'))
            publication_location = self.stringify(s.xpath('.//div/cite/span[@class="cit-pub-loc"]/text()'))
            citation_source = self.stringify(s.xpath('.//div/cite/span[@class="cit-source"]/text()'))
            date = self.stringify(s.xpath('.//div/cite/span[@class="cit-pub-date"]/text()'))
            journal = self.stringify(s.xpath('.//div/cite/abbr/text()'))
            doi = self.stringify(s.xpath('.//@data-doi'))
            links = self.cleanUrls(s.xpath('.//div/a'))
            pmed = self.setPubmedId(links)
            fp = self.stringify(s.xpath('.//div/cite/span[@class="cit-fpage"]/text()'))
            lp = self.stringify(s.xpath('.//div/cite/span[@class="cit-fpage"]/text()'))
            v = self.stringify(s.xpath('.//div/cite/span[@class="cit-vol"]/text()'))

            item = {
                'title': article_title,
                'publication': publication_name,
                'publication_location': publication_location,
                'citation_source': citation_source,
                'journal': journal,
                'links': links
            }

            if len(doi) > 0:
                item['doi'] = doi

            if len(fp) > 0 or len(lp) > 0:
                item['page'] = fp + '–' + lp,

            if str.isdigit(date):
                item['year'] = int(date)

            if str.isdigit(fp):
                item['first_page'] = int(fp)

            if str.isdigit(lp):
                item['last_page'] = int(lp)

            if str.isdigit(v):
                item['volume'] = int(v)

            if str.isdigit(pmed):
                item['pubmed_id'] = int(pmed)

            ref.append(dict((k, v) for k, v in item.items() if v))

        return ref

    def cleanUrls(self, strings):
        items = []
        for s in strings:
            raw = s.xpath('.//@href').extract()[0]
            text = self.stringify(s.xpath('.//text()'))

            if '{openurl}?' not in raw:

                if 'PubMed' or 'Web of Science' in raw:
                    parsed = urlparse(raw)
                    path = '{uri.path}'.format(uri=parsed)
                    query = parsed.query
                    params = dict(parse_qsl(query))
                    url = path
                else:
                    params = {}
                    path = ''

                url = raw
                items.append({
                    'text': text,
                    'url': url,
                    'path': path,
                    'params': params
                })
        return items

    def stringify(self, strings):
        return str.strip(''.join(strings.extract())).replace('\u00a0', ' ')

    def setPubmedId(self, listOfLinks):
        for l in listOfLinks:
            if l['text'] == 'PubMed':
                return l['params']['access_num']
        return ''

    def setInstitutions(self, listOfStrings):
        institutions = []
        for l in set(listOfStrings):
            i = list(map(str.strip, l.split(',')))
            # @TODO add geolocation data
            if len(i) > 1:
                tmp = {
                    'raw': l,
                    'country': i[-1],
                    'city': i[-2],
                    'address': ', '.join(i[1:-2]),
                    'head': i[0],
                }
                institutions.append(tmp)
        return institutions
