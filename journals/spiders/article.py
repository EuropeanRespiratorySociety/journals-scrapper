# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from journals.items import JournalsItem

from urllib.parse import urlparse
from urllib.parse import parse_qsl

# http://erj.ersjournals.com/sitemap.xml
# http://err.ersjournals.com/sitemap.xml
# http://breathe.ersjournals.com/sitemap.xml
# http://openres.ersjournals.com/sitemap.xml


class ArticleSpider(CrawlSpider):
    name = 'article'
    allowed_domains = [
        'erj.ersjournals.com',
        'openres.ersjournals.com',
        'err.ersjournals.com',
        'www.ersjournals.com',
        'breathe.ersjournals.com'
    ]
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
            'by/section/Cell',
            'external-ref?',
            '%7Bopenurl%7D?',
            '{openurl}?',
            'user/login',
            'by/section/',
            'section',
            'lookup'
            'lens/',
            'highwire/citation/',
            'panels_ajax_tab/',
            'ijlink'
            '\.pdf',
            '\.zip',
            '\.full.print',
            '\.print',
            '\.full',
            '\.full.pdf',
            '\.figures-only',
            '\.article-info',
            '\.abstract',
            '\.full.txt',
            '\..full-text.print',
            'expansion?')), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        i = {}
        i['page_url'] = response.url
        i['canonical'] = self.stringify(response.xpath('//link[@rel="canonical"]/@href'))
        i['journal_url'] = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(response.url))
        i['doi'] = self.stringify(response.xpath('//meta[@name="DC.Identifier"]/@content'))
        i['pubmed_id'] = self.stringify(response.xpath('//meta[@name="citation_pmid"]/@content'))
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
        i['publisher'] = self.stringify(response.xpath('//meta[@name="DC.Publisher"]/@content'))
        i['pisa'] = self.stringify(response.xpath('//meta[@name="HW.pisa"]/@content'))
        i['subjects'] = self.cleanUrls(response.xpath('//a[@class="highlight"]'))
        i['title'] = self.stringify(response.xpath('//meta[@name="citation_title"]/@content'))
        i['abstract'] = self.stringify(response.xpath('//meta[@name="og:description"]/@content'))
        i['short_abstract'] = self.stringify(response.xpath('//meta[@name="citation_abstract" and @scheme="short"]/@content'))
        i['full_available_text'] = ''.join(response.xpath('//div[@class="section"]/p').extract())
        i['references'] = self.cleanRef(response.xpath('//div[@class="section ref-list"]/ol/li/div'))
        return i

    def cleanRef(self, strings):
        ref = []
        for s in strings:
            article_title = self.stringify(s.xpath('.//div/cite/span[@class="cit-article-title"]/text()'))
            publication_name = self.stringify(s.xpath('.//div/cite/span[@class="cit-publ-name"]/text()'))
            publication_location = self.stringify(s.xpath('.//div/cite/span[@class="cit-pub-loc"]/text()'))
            citation_source = self.stringify(s.xpath('.//div/cite/span[@class="cit-source"]/text()'))
            pub_date = self.stringify(s.xpath('.//div/cite/span[@class="cit-pub-date"]/text()'))
            volume = self.stringify(s.xpath('.//div/cite/span[@class="cit-vol"]/text()'))
            page = self.stringify(s.xpath('.//div/cite/span[@class="cit-fpage"]/text()'))
            journal = self.stringify(s.xpath('.//div/cite/abbr/text()'))
            doi = self.stringify(s.xpath('.//@data-doi'))
            links = self.cleanUrls(s.xpath('.//div/a'))
            pubmed_id = self.setPubmedId(links)

            item = {
                'title': article_title,
                'publication': publication_name,
                'publication_location': publication_location,
                'citation_source': citation_source,
                'journal': journal,
                'year': pub_date,
                'volume': volume,
                'page': page,
                'doi': doi,
                'pubmed_id': pubmed_id,
                'links': links
            }
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
            institutions.append({
                'raw': l,
                'country': i[-1],
                'city': i[-2],
                'address': ', '.join(i[1:-2]),
                'head': i[0],
            })
        return institutions
