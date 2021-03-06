# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
import logging
import os

con = None

class AmazonPipeline(object):
    
    def __init__(self):
        self.setupDBCon()
        self.createTables()
        self.logger = logging.getLogger('padl')
        
    def setupDBCon(self):
        self.con = sqlite3.connect(os.getcwd() + '/amazon.db')
        self.cur = self.con.cursor()
    
    def createTables(self):
        self.dropAmazonTable()
        self.createAmazonTable()
    
    def dropAmazonTable(self):
        self.cur.execute("DROP TABLE IF EXISTS Amazon")
    
    def closeDB(self):
        self.con.close()
        
    def __del__(self):
        self.closeDB()
        
    def createAmazonTable(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS Amazon(id INTEGER PRIMARY KEY NOT NULL, \
            asin TEXT, \
            price TEXT, \
            category TEXT, \
            url TEXT \
            )")
    
    
    def process_item(self, item, spider):
        self.storeInDb(item)
        return item

    def storeInDb(self,item):
        self.cur.execute("INSERT INTO Amazon(\
            asin, \
            price, \
            category, \
            url \
            ) \
        VALUES( ?, ?, ?, ?)", \
        ( \
            item.get('Asin',''),
            item.get('Price',''),
            item.get('Category',''),
            item.get('Url','')
        ))
        self.con.commit()       