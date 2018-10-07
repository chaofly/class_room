# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request,FormRequest
from classRoom.items import ClassroomItem, ClassroomItemLoader
import re
import time
from urllib.parse import unquote

class HbutSpider(scrapy.Spider):
    name = 'hbut'
    allowed_domains = ['run.hbut.edu.cn']
    start_urls = ['http://run.hbut.edu.cn/ArrangeTask/RightPlaceSchedule/']

    headers = {
        "HOST":"run.hbut.edu.cn",
        "Referer":"run.hbut.edu.cn/",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def dealStr(self,myStr):
        num = int(myStr)
        num+=1
        if num<10:
            return "00"+str(num)
        elif num<100:
            return "101"
        elif num>100:
            left_num = num//100
            mid_num = num//10 - 10*left_num
            if mid_num>1:
                num=(left_num+1)*100 + 1
            return str(num)

    def parse(self, response):
        class_url = "http://run.hbut.edu.cn/ArrangeTask/RightPlaceSchedule?ClassRoom={0}"
        class_list = ("5B-","3-","2-","4-","工1-A","1-")
        for prefix in class_list:
            count = "0"
            while int(count)<900:
                count = self.dealStr(count)
                param = prefix + count
                current_url = class_url.format(param)
                yield scrapy.Request(current_url, headers=self.headers, meta={'cookiejar':True},callback=self.parse_detail)
                time.sleep(1)

    def deal_weeks(self,weeks_set):
        ini_set = {x for x in range(1,20)}
        for week_str in weeks_set:
            if "-" in week_str:
                border = re.match(r"(\d+)-(\d+)",week_str.strip(),re.S)
                left = int(border.group(1))
                right = int(border.group(2))
                for i in range(left,right+1):
                    ini_set = ini_set.difference(set([i]))
            elif "," in week_str:
                border = re.match(r"(\d+),(\d+)",week_str.strip(),re.S)
                left = int(border.group(1))
                right = int(border.group(2))
                ini_set = ini_set.difference(set([left,right]))
            else:    
                ini_set = ini_set.difference(set([int(week_str)]))
        return ini_set

    def deal_class(self,class_str):
        time_list = re.findall("<tr>(.*?)</tr>",class_str,re.S)
        my_items_list = []
        for times in time_list:
            class_time_obj = re.match(".*<th>第(.*?)节</th>",times,re.S)
            class_time = class_time_obj.group(1)
            days = re.findall("<td>(.*?)</td>",times,re.S)
            cnt = 0
            for day in days:
                cnt+=1
                weeks_list = re.findall(r"第(.*?)周",day,re.S)
                if len(weeks_list)==0:
                    for i in range(1,20):
                        my_items = {"place":"","types":"","times":class_time,"weeks_num":i,"days":cnt}
                        my_items_list.append(my_items)
                else:
                    weeks_set = set(weeks_list)
                    weeks_set = self.deal_weeks(weeks_set)
                    for week in weeks_set:
                        my_items = {"place":"","types":"","times":class_time,"weeks_num":week,"days":cnt}
                        my_items_list.append(my_items)
        return my_items_list

    def parse_detail(self,response):
        response_text = response.text
        if "周" in response_text:
            class_obj = re.match(".*?</tr>(.*</tr>)",response_text,re.S)
            class_list = self.deal_class(class_obj.group(1))
            place_obj = re.match(".*=(.*)",response.url,re.S)
            place = place_obj.group(1)
            if place[0]=='%':
                place = unquote(place, 'utf-8')
            for item in class_list:
                item['place'] = place
            
            for item in class_list:
                classroom_item = ClassroomItem()
                item_loader = ClassroomItemLoader(item=ClassroomItem(), response=response)
                item_loader.add_value("place", item["place"])
                item_loader.add_value("weeks_num", int(item["weeks_num"]))
                item_loader.add_value("days", int(item["days"]))
                item_loader.add_value("times", item["times"])
                item_loader.add_value("types", self.get_type(item["place"]))
                classroom_item = item_loader.load_item()
                yield classroom_item

    def get_type(self,place_str):
        switch_dict = {"1":1,"2":2,"3":3,"4":4,"5":5,"工":0,"%":0}
        return switch_dict[place_str[0]]

    def start_requests(self):
        return [Request('http://run.hbut.edu.cn/Account/LogOn',meta={'cookiejar':1},callback=self.getValiCode)]

    def getValiCode(self,response):
        return [Request('http://run.hbut.edu.cn/Account/GetValidateCode',meta={'cookiejar':response.meta['cookiejar']},callback=self.login)]

    def login(self,response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass
        post_data = {
            "isRemember":"1",
            "Role":	"Student",
            "UserName":"1510300124",
            "Password":"54chaochao*",
            "ValidateCode":" "
        }

        captcha = input("输入验证码\n>")
        post_url = "http://run.hbut.edu.cn/Account/LogOn"
        post_data["ValidateCode"] = str(captcha).strip()

        return [scrapy.FormRequest(
            url=post_url,
            meta = {'cookiejar':response.meta['cookiejar']},
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self,response):
        response_text = response.text
        if "屈超" in response_text:
            for url in self.start_urls:
                yield scrapy.Request(url,meta={'cookiejar':True},dont_filter=True,headers=self.headers)
        else:
            assert("错误")
