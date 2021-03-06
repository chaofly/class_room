# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from openpyxl import Workbook

class ClassroomPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常
        return item

    def handle_error(self, failure, item, spider):
        #处理异步插入的异常
        print (failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_sql()
        cursor.execute(insert_sql, params) 
        #params = [item["place"],item["weeks_num"],item["days"],item["times"],item["types"]]
        #cursor.execute(insert_sql, ([item["place"],item["weeks_num"],item["days"],item["times"],item["types"]))

# class ExcelPipeline(object):
#     def __init__(self):
#         self.wb = Workbook()
#         self.ws = self.wb.active

#         self.ws.append(['周数','星期几','时间','地点'])
    
#     def process_item(self,item,spider):
#         line = [str(item['weeks_num']),str(item['days']),str(item['times']),str(item['place'])]
#         self.ws.append(line)
#         self.wb.save("class_room.xlsx")
#         return item