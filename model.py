import json
import logging
import os
import shutil

import lxml.html
import requests

import init_service
from config import *


class ModelByInn:
    def __init__(self, inn, anticaptcha):
        self.inn = inn
        self.id_captcha = ''
        self.anticaptcha = anticaptcha

    def return_arb(self):
        result = self.try_get_captcha()
        if not result:
            raise Exception("the captcha was not gotten")
        txt_first_page = self.get_instances()
        max_page = self.num_page(txt_first_page)
        if max_page > 1:
            items_list = self.extract_all_pages(txt_first_page, max_page)
            return items_list
        else:
            items_list = self.extract_items(txt_first_page)
            return items_list

    def extract_all_pages(self, firs_page, num_page):
        full_list = self.extract_items(firs_page)
        for p in range(2, (num_page + 1)):
            result = self.try_get_captcha()
            if not result:
                raise Exception("the captcha was not gotten")
            txt_page = self.get_instances(p)
            items_list = self.extract_items(txt_page)
            full_list.extend(items_list)
        return full_list

    def get_instances(self, page=1):
        data = '{"Page":' + str(
                page) + ',"Count":25' + (
                   ',"CaseType":"B"' if not all_items else '') + ',"Courts":[],"DateFrom":null,"DateTo":null,"Sides":[{"Name":"' + self.inn + '","Type":-1,"ExactMatch":false}],"Judges":[],"CaseNumbers":[],"WithVKSInstances":false}'
        instance_headers['RecaptchaToken'] = self.id_captcha
        r = requests.post('http://kad.arbitr.ru/Kad/SearchInstances',
                          headers=instance_headers, data=data)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            raise Exception("error in function get_instances, status code is not 200")
        return r.text

    def num_page(self, t):
        tree = lxml.html.document_fromstring(t)
        document_page_count = tree.xpath('//input[@id = "documentsPagesCount"]')[0].get('value')
        return int(document_page_count)

    def extract_items(self, txt):
        tree = lxml.html.document_fromstring(txt)
        elements = []
        items = tree.xpath('//tr')
        for el in items:
            item = self.create_item(el)
            elements.append(item)
        return elements

    def create_item(self, el):
        item = {}
        url = el.xpath('.//a')[0].get('href').strip(' \t\n')
        item['url'] = url
        num = el.xpath('.//a')[0].text.replace('\t', '').replace('\r', '').replace('\n', '').strip(' \t\n')
        item['num'] = num
        date = el.xpath('.//a/preceding-sibling::div/span')[0].text.replace('\t', '').replace('\r', '').replace(
                '\n',
                '').strip(
                ' \t\n')
        item['date'] = date
        plaintiff_text = el.xpath('.//td[@class = "plaintiff"]')[
            0].text_content().replace('\t', '').replace('\r', '').replace('\n', '').strip(' \t\n')
        if self.inn in plaintiff_text:
            is_plaintiff = 1
        else:
            is_plaintiff = 0
        item['is_plaintiff'] = is_plaintiff
        respondent_text = el.xpath('.//td[@class = "respondent"]')[
            0].text_content().replace('\t', '').replace('\r', '').replace('\n', '').strip(' \t\n')
        if self.inn in respondent_text:
            is_respondent = 1
        else:
            is_respondent = 0
        item['is_respondent'] = is_respondent
        return item

    def try_get_captcha(self):
        try_count = 10
        while True:
            if try_count < 0:
                return False
            if self.if_need_captcha():
                try:
                    if self.get_captcha():
                        return True
                except Exception as e:
                    logging.error(e)
                try_count -= 1
            else:
                return True

    def if_need_captcha(self):
        r = requests.post('http://kad.arbitr.ru/Recaptcha/IsNeedShowCaptcha?_=1571051816364',
                          headers=base_headers)
        text_json = r.text
        if text_json == "":
            raise Exception("error in function if_need_captcha, empty response")
        json_data = json.loads(text_json)
        if not json_data['Success']:
            raise Exception("error in function if_need_captcha, success is not true")
        if json_data['Result']:
            return True
        return False

    def get_captcha(self):
        r = requests.post('http://kad.arbitr.ru/Recaptcha/GetCaptchaId?_=1571051816364',
                          headers=base_headers)
        text_json = r.text
        if text_json == "":
            raise Exception("error in function get_captcha, empty response")
        json_data = json.loads(text_json)
        if not json_data['Success']:
            raise Exception("error in function get_captcha, success is not true")
        captcha_id = json_data['Result']
        return self.download_captcha(captcha_id)

    def download_captcha(self, captcha_id):
        url = f"http://kad.arbitr.ru/Recaptcha/GetImage/{captcha_id}"
        path_image = os.path.join(init_service.EXECUTE_PATH, init_service.TEMP_D, f"{captcha_id}.jpeg")
        response = requests.get(url, stream=True, headers=base_headers)
        with open(path_image, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        text = self.anticaptcha.img_to_text(path_image)
        # print('input captcha')
        # text = input()  # this need add anticaptcha
        os.remove(path_image)
        return self.check_captcha(captcha_id, text)

    def check_captcha(self, captcha_id, text):
        url = f"http://kad.arbitr.ru/Recaptcha/CheckCaptcha?_=1571054501055&id={captcha_id}&text={text}"
        r = requests.post(url, headers=base_headers)
        text_json = r.text
        if text_json == "":
            raise Exception("error in function check_captcha, empty response")
        json_data = json.loads(text_json)
        if not json_data['Success']:
            raise Exception("error in function get_captcha, success is not true")
        self.id_captcha = captcha_id
        return json_data['Result']
