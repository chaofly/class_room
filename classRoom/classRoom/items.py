# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ClassroomItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    place = scrapy.Field()
    weeks_num = scrapy.Field()
    days = scrapy.Field()
    times = scrapy.Field()
    types = scrapy.Field()

    def get_sql(self):
        insert_sql = """
             insert into class_room3(place,weeks_num , days, times,types)
             VALUES (%s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE types=VALUES(types)
         """
        params = (self["place"],self["weeks_num"],self["days"],self["times"],self["types"])

        return insert_sql,params

    # tags = scrapy.Field(
    #     input_processor=MapCompose(remove_comment_tags),
    #     output_processor=Join(",")
    # )
class ClassroomItemLoader(ItemLoader):
    #自定义itemloader
    #default_output_processor = TakeFirst()
    pass