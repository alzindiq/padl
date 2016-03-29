# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import re

class PriceParser(object):

    selectors = {}
    diagnostics = {}

    thisDir = os.path.abspath(os.path.dirname(__file__))
    logConfigFile = os.path.join(thisDir, './config', 'logging_config.ini')
    logging.config.fileConfig(logConfigFile)

    logger = logging.getLogger(__name__)
    # look for <b>Price:</b>&nbsp;£9.49&nbsp;
    priceRE = re.compile(ur'<b>Price:</b>&nbsp;([£\$€]?\d*\.\d+|\d+)')

    def __init__(self):
        self._build_selectors()
        self._init_diagnostics()

    def get_price(self,response,currency=ur'£'):
        for name, selector in self.selectors.iteritems():
            priceText = response.xpath(selector).extract()
            if priceText:
                self.diagnostics[name] += 1
                break

        if not priceText:

            # try regexes
            print "regex"
            price= self.priceRE.findall(response.body)
            print price
            if price:
                return price
            else:
                self.logger.debug("Could not find a selector for ", response.url)
                failed = os.path.join(self.thisDir, './failed/noSelector', hashlib.md5(response.url.encode()).hexdigest())
                f = open(failed,'w')
                f.write(response.url)
                f.write('\n')
                f.write(response.body)
                f.close()
                return 0
        else:
            priceArray= self._find_prices(priceText,currency)
            if(len(priceArray)==1):
                price = priceArray[0]
            else:
                noTextPrice= self._filter_text(priceArray)
                if(len(noTextPrice)==1):
                    price = noTextPrice[0]
                else:
                    self.logger.info('Could not get price of ', response.url)
                    failed = os.path.join(self.thisDir, './failed/wrongPrice', hashlib.md5(response.url.encode()).hexdigest())
                    f = open(failed,'w')
                    f.write(priceArray)
                    f.write('\n')
                    f.write(response.body)
                    f.close()
                    price = 0
            return price

    def _find_prices(self, text, currency):
        prices = []
        for priceDiv in text:
            indx = priceDiv.find(currency)
            if indx != -1:
                if ("on orders over" not in priceDiv):
                    prices.append(priceDiv[indx + 1:])
        return prices

    def _filter_text(self, array):
        noText = []
        for s in array:
            print s
            if self._is_number(s):
                noText.append(s)
        return noText

    def _is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            int(s)
            return True
        except ValueError:
            pass

        return False

    def _build_selectors(self):

        self.selectors['ourprice']='//*[contains(@id,"priceblock_ourprice")]//text()'
        self.selectors['ourprice_table_tr2']='//div[contains(@id,"price")]/table/tr[2]/' \
                                             'span[contains(@id,"priceblock_ourprice")]//text()'
        self.selectors['ourprice_table_tr1']='//div[contains(@id,"price")]/table/tr[1]/' \
                                             'span[contains(@id,"priceblock_ourprice")]//text()'
        self.selectors['ourprice_table_tbody_tr2']='//div[contains(@id,"price")]/table/tbody/tr[2]/' \
                                                   'span[contains(@id,"priceblock_ourprice")]//text()'
        self.selectors['ourprice_table_tbody_tr1']='//div[contains(@id,"price")]/table/tbody/tr[1]/' \
                                                   'span[contains(@id,"priceblock_ourprice")]//text()'
        self.selectors['ourprice_table_tbody_tr2_td2']='//div[contains(@id,"price")]/table/tbody/tr[2]/td[2]/' \
                                                       'span[contains(@id,"priceblock_ourprice")]//text()'
        self.selectors['ourprice_table_tbody_tr1_td2']='//div[contains(@id,"price")]/table/tbody/tr[1]/td[2]/' \
                                                       'span[contains(@id,"priceblock_ourprice")]//text()'

        self.selectors['saleprice']='//*[@id="priceblock_saleprice"]//text()'
        self.selectors['saleprace_table_tr2_td']='//div[contains(@id,"price")]/table/tr[2]/td/' \
                                                 'span[contains(@id,"priceblock_saleprice")]//text()'
        self.selectors['saleprice_table_tr1_td']='//div[contains(@id,"price")]/table/tr[1]/td/' \
                                                 'span[contains(@id,"priceblock_saleprice")]//text()'

        self.selectors['price_table_tbody_tr1_td']='//div[contains(@id,"price")]/table/tbody/tr[1]/td/' \
                                                   'span[contains(@id,"priceblock_saleprice")]//text()'
        self.selectors['price_table_tbody_tr2_td']='//div[contains(@id,"price")]/table/tbody/tr[2]/td/' \
                                                   'span[contains(@id,"priceblock_saleprice")]//text()'
        self.selectors['price_table_tr2_td']='//div[contains(@id,"price")]/table/tr[2]/td/' \
                                             'span[contains(@id,"priceblock_dealprice")]//text()'
        self.selectors['price_table_tr1_td']='//div[contains(@id,"price")]/table/tr[1]/td/' \
                                             'span[contains(@id,"priceblock_dealprice")]//text()'
        self.selectors['price_table_tr2_td2_nospan']='//table[contains(@id,"price")]/tr[2]/td[2]//text()'

        self.selectors['dealprice']='//*[@id="priceblock_dealprice"]//text()'
        self.selectors['dealprice_table_tbody_tr2_td']='//div[contains(@id,"price")]/table/tbody/tr[2]/td/' \
                                                       'span[contains(@id,"priceblock_dealprice")]//text()'
        self.selectors['dealprice_table_tbody_tr1_td']='//div[contains(@id,"price")]/table/tbody/tr[1]/td/' \
                                                       'span[contains(@id,"priceblock_dealprice")]//text()'

        self.selectors['aloha']='//*[@id="alohaVariations_feature_div"]/div[@id="aloha-variations"]' \
                                '/div[@id="variation_transaction_type"]/ul/li[contains(@id,"transaction_type_2")]' \
                                '/div[@class="device-price"]/span[@class="our-price"]//text()'

         #self.selectors['aloha_deep']='//div[@id="variation_transaction_type"]/ul/li[@id="transaction_type_2"]' \
         #                       '/div[@class="device-price"]/span[@class="our-price"]//text()'

        self.selectors['pricetable']='//table[@id="price"]/tr[2]/td[2]/span[contains(@id,"price")]//text()'

        self.selectors['dpprice']='//table[contains(@class,"dpPrice")]/tr[2]/td[2]/' \
                                  'span[contains(@class,"dpOurPrice")]//text()'

        self.selectors['dpprice_tr1']='//table[contains(@class,"dpPrice")]/tr[1]/td[2]/' \
                                  'span[contains(@class,"dpOurPrice")]//text()'

        self.logger.info("Loaded all selectors")

    def _init_diagnostics(self):
        self.diagnostics['ourprice'] = 0
        self.diagnostics['ourprice_table_tr2'] = 0
        self.diagnostics['ourprice_table_tr1'] = 0
        self.diagnostics['ourprice_table_tbody_tr2'] = 0
        self.diagnostics['ourprice_table_tbody_tr1'] = 0
        self.diagnostics['ourprice_table_tbody_tr2_td2'] = 0
        self.diagnostics['ourprice_table_tbody_tr1_td2'] = 0

        self.diagnostics['saleprice'] = 0
        self.diagnostics['saleprace_table_tr2_td'] = 0
        self.diagnostics['saleprice_table_tr1_td'] = 0

        self.diagnostics['price_table_tbody_tr1_td'] = 0
        self.diagnostics['price_table_tbody_tr2_td'] = 0
        self.diagnostics['price_table_tr2_td'] = 0
        self.diagnostics['price_table_tr1_td'] = 0

        self.diagnostics['dealprice'] = 0
        self.diagnostics['dealprice_table_tbody_tr2_td'] = 0
        self.diagnostics['dealprice_table_tbody_tr1_td'] = 0

        self.diagnostics['aloha'] = 0

        self.diagnostics['pricetable'] = 0

        self.diagnostics['dpprice'] = 0

        self.diagnostics['dpprice_tr1'] = 0

        self.diagnostics['price_table_tr2_td2_nospan'] = 0

    def log_selector_diagnostics(self):
        for key, value in self.selectors:
            self.logger.info(key,'->',value)

