import base64
import json
import logging
import os
import shutil
import time

import lxml.html
import requests

import init_service
from secret_keys import *

id_captcha = ""


def return_arb(inn):
    result = try_get_captcha()
    if not result:
        raise Exception("the captcha was not gotten")
    txt_first_page = get_instances(inn)
    max_page = num_page(txt_first_page)
    if max_page > 1:
        items_list = extract_all_pages(txt_first_page, max_page, inn)
        return items_list
    else:
        items_list = extract_items(txt_first_page)
        return items_list


def extract_all_pages(firs_page, num_page, inn):
    full_list = extract_items(firs_page)
    for p in range(2, (num_page + 1)):
        result = try_get_captcha()
        if not result:
            raise Exception("the captcha was not gotten")
        txt_page = get_instances(inn, p)
        items_list = extract_items(txt_page)
        full_list.extend(items_list)
    return full_list


def get_instances(inn, page=1):
    data = '{"Page":' + str(
            page) + ',"Count":25,"Courts":[],"DateFrom":null,"DateTo":null,"Sides":[{"Name":"' + inn + '","Type":-1,"ExactMatch":false}],"Judges":[],"CaseNumbers":[],"WithVKSInstances":false}'
    instance_headers['RecaptchaToken'] = id_captcha
    r = requests.post('http://kad.arbitr.ru/Kad/SearchInstances',
                      headers=instance_headers, data=data)
    if r.status_code != 200:
        raise Exception("error in function get_instances, status code is not 200")
    return r.text


def num_page(t):
    tree = lxml.html.document_fromstring(t)
    document_page_count = tree.xpath('//input[@id = "documentsPagesCount"]')[0].get('value')
    return int(document_page_count)


def extract_items(txt):
    tree = lxml.html.document_fromstring(txt)
    elements = []
    items = tree.xpath('//tr')
    for el in items:
        item = {}
        url = el.xpath('.//a')[0].get('href').strip(' \t\n')
        item['url'] = url
        num = el.xpath('.//a')[0].text.replace('\t', '').replace('\r', '').replace('\n', '').strip(' \t\n')
        item['num'] = num
        date = el.xpath('.//a/preceding-sibling::div/span')[0].text.replace('\t', '').replace('\r', '').replace('\n',
                                                                                                                '').strip(
                ' \t\n')
        item['date'] = date
        elements.append(item)
    return elements


def try_get_captcha():
    try_count = 10
    while True:
        if try_count < 0:
            return False
        if if_need_captcha():
            try:
                if get_captcha():
                    return True
            except Exception as e:
                logging.error(e)
            try_count -= 1
        else:
            return True


def if_need_captcha():
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


def get_captcha():
    r = requests.post('http://kad.arbitr.ru/Recaptcha/GetCaptchaId?_=1571051816364',
                      headers=base_headers)
    text_json = r.text
    if text_json == "":
        raise Exception("error in function get_captcha, empty response")
    json_data = json.loads(text_json)
    if not json_data['Success']:
        raise Exception("error in function get_captcha, success is not true")
    captcha_id = json_data['Result']
    return download_captcha(captcha_id)


def download_captcha(captcha_id):
    url = f"http://kad.arbitr.ru/Recaptcha/GetImage/{captcha_id}"
    path_image = os.path.join(init_service.EXECUTE_PATH, init_service.TEMP_D, f"{captcha_id}.jpeg")
    response = requests.get(url, stream=True, headers=base_headers)
    with open(path_image, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    text = anticaptcha(path_image)
    # print('input captcha')
    # text = input()  # this need add anticaptcha
    os.remove(path_image)
    return check_captcha(captcha_id, text)


def check_captcha(captcha_id, text):
    global id_captcha
    url = f"http://kad.arbitr.ru/Recaptcha/CheckCaptcha?_=1571054501055&id={captcha_id}&text={text}"
    r = requests.post(url, headers=base_headers)
    text_json = r.text
    if text_json == "":
        raise Exception("error in function check_captcha, empty response")
    json_data = json.loads(text_json)
    if not json_data['Success']:
        raise Exception("error in function get_captcha, success is not true")
    id_captcha = captcha_id
    return json_data['Result']


def anticaptcha(path_image):
    encoded_string = ''
    with open(path_image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    url = 'https://rucaptcha.com/in.php'
    data = {'key': API_KEY, 'method': 'base64', 'lang': 'ru', 'json': 1, 'regsense': 1,
            'body': encoded_string}
    r = requests.post(url, data=data)
    json_data = json.loads(r.text)
    if json_data['status'] != 1:
        raise Exception('status service anticaptcha is not 1')
    return get_response_anticaptcha(json_data['request'])


def get_response_anticaptcha(req_id):
    url = f'https://rucaptcha.com/res.php?key={API_KEY}&action=get&id={req_id}&json=1'
    num_try = 20
    while True:
        if num_try < 0:
            raise Exception('cannot get response anticaptcha after 20 attempts')
        try:
            r = requests.get(url)
            json_data = json.loads(r.text)
            if json_data['status'] != 1:
                raise Exception(json_data['request'])
            print(json_data['request'])
            return json_data['request']
        except Exception as e:
            logging.error(e)
            time.sleep(5)
        num_try -= 1
