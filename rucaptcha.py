import base64
import json
import logging
import time

import requests


class Rucaptcha:

    def __init__(self, api_key):
        self.api_key = api_key

    def img_to_text(self, path_image):
        with open(path_image, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        url = 'https://rucaptcha.com/in.php'
        data = {'key': self.api_key, 'method': 'base64', 'lang': 'ru', 'json': 1, 'regsense': 1,
                'body': encoded_string}
        r = requests.post(url, data=data)
        json_data = json.loads(r.text)
        if json_data['status'] != 1:
            raise Exception('status service anticaptcha is not 1')
        return self.get_response(json_data['request'])

    def get_response(self, req_id):
        url = f'https://rucaptcha.com/res.php?key={self.api_key}&action=get&id={req_id}&json=1'
        num_try = 20
        while True:
            if num_try < 0:
                raise Exception('cannot get response anticaptcha after 20 attempts')
            try:
                r = requests.get(url)
                json_data = json.loads(r.text)
                if json_data['status'] != 1:
                    raise Exception(json_data['request'])
                return json_data['request']
            except Exception as e:
                logging.error(e)
                time.sleep(5)
            num_try -= 1
