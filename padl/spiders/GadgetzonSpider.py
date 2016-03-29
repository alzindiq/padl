# -*- coding: utf-8 -*-
import logging
import re
import scrapy
import os
from scrapy.utils.log import configure_logging
from padl import items
from padl import price_parser

class GadgetzonSpider(scrapy.Spider):
    name = "gadgetzone"
    allowed_domains = ["amazon.com", "amazon.co.uk", "dmoz.org"]
    asinRE = re.compile(ur'dp/[a-zA-Z0-9]{10,}')

    def __init__(self, seedUrl='http://www.amazon.co.uk/gp/bestsellers/electronics?ie=UTF8&ref_=sv_ce_0'):
        print "Starting gadgetzon spider"
        self.seedUrl = seedUrl
        configure_logging(install_root_handler=False)
        self.thisDir = os.path.abspath(os.path.dirname(__file__))
        logConfigFile = os.path.join(self.thisDir, 'gadget.log')
        logging.basicConfig(
            filename=logConfigFile,
            format='%(asctime)s - %(name)s - %(levelname)s - %(module)s : %(lineno)d - %(message)s',
            level=logging.DEBUG
        )
        self.price_parser = price_parser.PriceParser()

    def start_requests(self):
        yield scrapy.Request(self.seedUrl, self.parse)

    def parse(self, response):
        urls = response.xpath('//div[contains(@class,"zg_title")]//a/@href').extract()
        for url in urls:
            yield scrapy.Request(str(url).strip(),self.parseItem)

    def parseItem(self,response):
        self.logger.info(response)
        item = items.AmazonItem()
        price = self.price_parser.get_price(response,ur'£')
        item['Price'] = price
        item['Asin'] = self._find_asin(response.url)
        item['Category'] = 'electronics'
        item['Url'] = response.url
        yield item

    def _find_asin(self,url):
        num=re.search(self.asinRE, url).group(0)
        return str(num)[3:]

