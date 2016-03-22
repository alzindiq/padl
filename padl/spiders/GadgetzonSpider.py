# -*- coding: utf-8 -*-
import scrapy
import logging
import os
import re
from logging.config import fileConfig
logger = logging.getLogger(__name__)

class GadgetzonSpider(scrapy.Spider):
    name = "gadgetzon"
    allowed_domains = ["amazon.com", "amazon.co.uk", "dmoz.org"]

    moneyRE = re.compile(ur'\£(\d*\.\d{1,2})')
    #re.compile(ur'£(\d*\.\d{1,2})')
    #moneyRE = re.compile(ur'£(\d*?:\.\d{2})')

    def __init__(self, seedUrl='http://www.amazon.co.uk/gp/bestsellers/electronics?ie=UTF8&ref_=sv_ce_0'):
        logger.info("Starting gadgetzon spider")
        thisDir = os.path.abspath(os.path.dirname(__file__))
        logConfigFile = os.path.join(thisDir, '../config', 'logging_config.ini')
        fileConfig(logConfigFile)
        self.seedUrl = seedUrl


    def start_requests(self):
        yield scrapy.Request(self.seedUrl, self.parse)


    def parse(self, response):
        urls = response.xpath('//div[contains(@class,"zg_title")]//a/@href').extract()
        for url in urls:
            yield scrapy.Request(str(url).strip(),self.parseItem)


    def parseItem(self,response):
        print response
        text = response.xpath('//span[contains(@id,"price")]//text()').extract()
        #print "ASIN "+self.findAsin(response.url)
        print self.find_prices(text)

    def find_prices(self, text):
        prices = []
        for priceDiv in text:
            indx = priceDiv.find(ur'£')
            if indx != -1:
                prices.append(priceDiv[indx + 1:])

        return prices

    def findAsin(self,url):
        num=re.search(self.asinRE, url).group(0)
        return str(num)[4:]

